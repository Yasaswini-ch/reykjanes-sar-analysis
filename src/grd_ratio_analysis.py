import os
import click
import numpy as np
import rasterio as rio
from rasterio.windows import from_bounds as win_from_bounds, transform as win_transform, Window
from rasterio.warp import transform_bounds
import matplotlib.pyplot as plt


def read_band(path):
    with rio.open(path) as ds:
        arr = ds.read(1).astype('float32')
        profile = ds.profile
    return arr, profile


def write_tif(path, arr, profile):
    p = profile.copy()
    p.update(dtype='float32', count=1, compress='deflate')
    with rio.open(path, 'w', **p) as dst:
        dst.write(arr.astype('float32'), 1)


def _round_window(win: Window) -> Window:
    """Round a Window's offsets to floor and sizes to floor to ensure integer indices."""
    col_off = int(np.floor(win.col_off))
    row_off = int(np.floor(win.row_off))
    width = int(np.floor(win.width))
    height = int(np.floor(win.height))
    return Window(col_off, row_off, width, height)


def _compute_common_windows(pre_path: str, post_path: str):
    """
    Compute raster windows for the overlapping extent between two rasters.
    Returns (window_pre, window_post, out_profile_base) where windows index the
    overlap for each raster, and out_profile_base contains CRS/transform/size based
    on the pre raster's grid.
    """
    with rio.open(pre_path) as da, rio.open(post_path) as db:
        # Express both bounds in pre raster CRS
        if da.crs != db.crs:
            b_pre = da.bounds
            b_post_in_pre = transform_bounds(db.crs, da.crs, *db.bounds, densify_pts=21)
        else:
            b_pre = da.bounds
            b_post_in_pre = db.bounds

        # Intersection bounds in pre CRS
        left = max(b_pre.left, b_post_in_pre[0])
        bottom = max(b_pre.bottom, b_post_in_pre[1])
        right = min(b_pre.right, b_post_in_pre[2])
        top = min(b_pre.top, b_post_in_pre[3])
        if not (left < right and bottom < top):
            raise ValueError('No overlapping extent between rasters')

        # Windows in each dataset
        win_pre = win_from_bounds(left, bottom, right, top, transform=da.transform)

        # Compute the same intersection bounds in post CRS
        inter_in_post = transform_bounds(da.crs, db.crs, left, bottom, right, top, densify_pts=21)
        win_post = win_from_bounds(inter_in_post[0], inter_in_post[1], inter_in_post[2], inter_in_post[3], transform=db.transform)

        # Round to integer pixel windows (compat helper)
        win_pre = _round_window(win_pre)
        win_post = _round_window(win_post)

        # Harmonize sizes (min of both, anchored at top-left)
        h = int(min(win_pre.height, win_post.height))
        w = int(min(win_pre.width, win_post.width))
        win_pre = Window(win_pre.col_off, win_pre.row_off, w, h)
        win_post = Window(win_post.col_off, win_post.row_off, w, h)

        out_transform = win_transform(win_pre, da.transform)
        out_profile_base = {
            'crs': da.crs,
            'transform': out_transform,
            'width': w,
            'height': h,
        }
        return win_pre, win_post, out_profile_base


def crop_to_common_extent(pre_path: str, post_path: str):
    """
    Read two rasters and crop them to their common overlapping extent.
    Returns (pre_arr, post_arr, out_profile_base) with matching shapes.
    """
    win_pre, win_post, out_prof = _compute_common_windows(pre_path, post_path)
    with rio.open(pre_path) as da, rio.open(post_path) as db:
        pre_arr = da.read(1, window=win_pre).astype('float32')
        post_arr = db.read(1, window=win_post).astype('float32')
    return pre_arr, post_arr, out_prof


@click.command()
@click.option('--pre', 'pre_vv', required=True, help='Pre-event VV GeoTIFF')
@click.option('--prevh', 'pre_vh', required=True, help='Pre-event VH GeoTIFF')
@click.option('--post', 'post_vv', required=True, help='Post-event VV GeoTIFF')
@click.option('--postvh', 'post_vh', required=True, help='Post-event VH GeoTIFF')
@click.option('--outdir', default='outputs', show_default=True)
@click.option('--quicklook', is_flag=True, help='Save PNG quicklooks')
def main(pre_vv, pre_vh, post_vv, post_vh, outdir, quicklook):
    os.makedirs(outdir, exist_ok=True)
    # Compute a common crop window using VV rasters and apply to both VV and VH
    try:
        win_pre, win_post, out_base = _compute_common_windows(pre_vv, post_vv)
    except Exception:
        # Fallback to full read if windows cannot be computed (should be rare)
        win_pre = win_post = None
        out_base = None

    if win_pre is not None and win_post is not None:
        with rio.open(pre_vv) as ds:
            profile_full = ds.profile
        pre_vv_arr = rio.open(pre_vv).read(1, window=win_pre).astype('float32')
        pre_vh_arr = rio.open(pre_vh).read(1, window=win_pre).astype('float32')
        post_vv_arr = rio.open(post_vv).read(1, window=win_post).astype('float32')
        post_vh_arr = rio.open(post_vh).read(1, window=win_post).astype('float32')
        # Build profile from base
        profile = profile_full.copy()
        profile.update(
            width=out_base['width'], height=out_base['height'], transform=out_base['transform']
        )
    else:
        pre_vv_arr, profile = read_band(pre_vv)
        pre_vh_arr, _ = read_band(pre_vh)
        post_vv_arr, _ = read_band(post_vv)
        post_vh_arr, _ = read_band(post_vh)

    eps = 1e-6
    pre_ratio_db = 10*np.log10((pre_vh_arr + eps) / (pre_vv_arr + eps))
    post_ratio_db = 10*np.log10((post_vh_arr + eps) / (post_vv_arr + eps))
    # Ensure shapes match (defensive cropping to min common shape)
    if pre_ratio_db.shape != post_ratio_db.shape:
        h = min(pre_ratio_db.shape[0], post_ratio_db.shape[0])
        w = min(pre_ratio_db.shape[1], post_ratio_db.shape[1])
        pre_ratio_db = pre_ratio_db[:h, :w]
        post_ratio_db = post_ratio_db[:h, :w]
        # Update profile dims if needed
        profile = profile.copy()
        profile.update(width=w, height=h)
    delta_ratio = post_ratio_db - pre_ratio_db

    write_tif(os.path.join(outdir, 'VH_VV_ratio_pre.tif'), pre_ratio_db, profile)
    write_tif(os.path.join(outdir, 'VH_VV_ratio_post.tif'), post_ratio_db, profile)
    write_tif(os.path.join(outdir, 'delta_ratio_db.tif'), delta_ratio, profile)

    if quicklook:
        import matplotlib.pyplot as plt
        for name, arr, cmap, vmin, vmax in [
            ('VH_VV_ratio_pre.png', pre_ratio_db, 'viridis', None, None),
            ('VH_VV_ratio_post.png', post_ratio_db, 'viridis', None, None),
            ('delta_ratio_db.png', delta_ratio, 'RdBu', -5, 5),
        ]:
            plt.figure(figsize=(6,5))
            plt.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
            plt.colorbar()
            plt.title(name)
            plt.tight_layout()
            plt.savefig(os.path.join(outdir, name), dpi=200)
            plt.close()

    print('Saved ratio products to', outdir)


if __name__ == '__main__':
    main()
