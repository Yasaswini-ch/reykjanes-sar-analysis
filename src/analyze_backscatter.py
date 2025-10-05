"""
Analyze Sentinel-1 GRD RTC outputs: compute VH/VV ratio, changes, and plots.

Usage examples:
  python src/analyze_backscatter.py --manifest data/rtc/manifest.csv --output-dir outputs/

This script expects a manifest CSV with columns: filename,date,polarization,period
It pairs VV and VH from the same granule/date within each period.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
import csv
import math
import click
import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt


def _read_band(path: Path) -> Tuple[np.ndarray, dict]:
    with rio.open(path) as ds:
        arr = ds.read(1).astype('float32')
        prof = ds.profile
        nodata = ds.nodata
    if nodata is not None:
        arr = np.where(arr == nodata, np.nan, arr)
    return arr, prof


def _write_tif(path: Path, arr: np.ndarray, profile: dict) -> None:
    p = profile.copy()
    p.update(dtype='float32', count=1, compress='deflate')
    path.parent.mkdir(parents=True, exist_ok=True)
    with rio.open(path, 'w', **p) as dst:
        dst.write(arr.astype('float32'), 1)


def compute_vh_vv_ratio(vv_tif: Path, vh_tif: Path, output_tif: Path) -> None:
    """Compute 10*log10(VH/VV) with epsilon for stability."""
    vh, prof = _read_band(vh_tif)
    vv, _ = _read_band(vv_tif)
    eps = 1e-6
    ratio_db = 10.0 * np.log10((vh + eps) / (vv + eps))
    _write_tif(output_tif, ratio_db, prof)


def compute_change(pre_ratio_tif: Path, post_ratio_tif: Path, output_tif: Path) -> Dict[str, float]:
    pre, prof = _read_band(pre_ratio_tif)
    post, _ = _read_band(post_ratio_tif)
    delta = post - pre
    delta = np.clip(delta, -10.0, 10.0)
    _write_tif(output_tif, delta, prof)
    vals = delta[np.isfinite(delta)]
    if vals.size == 0:
        return {'mean': float('nan'), 'std': float('nan'), 'p5': float('nan'), 'p95': float('nan')}
    return {
        'mean': float(np.nanmean(vals)),
        'std': float(np.nanstd(vals)),
        'p5': float(np.nanpercentile(vals, 5)),
        'p95': float(np.nanpercentile(vals, 95)),
    }


def plot_comparison(pre_tif: Path, post_tif: Path, delta_tif: Path, output_png: Path) -> None:
    pre, _ = _read_band(pre_tif)
    post, _ = _read_band(post_tif)
    delta, _ = _read_band(delta_tif)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
    im0 = axes[0].imshow(pre, cmap='RdYlGn')
    axes[0].set_title('VH/VV (pre) [dB]'); axes[0].axis('off')
    fig.colorbar(im0, ax=axes[0], shrink=0.7)

    im1 = axes[1].imshow(post, cmap='RdYlGn')
    axes[1].set_title('VH/VV (post) [dB]'); axes[1].axis('off')
    fig.colorbar(im1, ax=axes[1], shrink=0.7)

    im2 = axes[2].imshow(delta, cmap='RdBu_r', vmin=-10, vmax=10)
    axes[2].set_title('Δ VH/VV (post - pre) [dB]'); axes[2].axis('off')
    fig.colorbar(im2, ax=axes[2], shrink=0.7)

    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=150)
    plt.close(fig)


def _parse_pol_from_name(path: Path) -> Optional[str]:
    name = path.stem.upper()
    if name.endswith('_VV') or '_VV_' in name:
        return 'VV'
    if name.endswith('_VH') or '_VH_' in name:
        return 'VH'
    return None


def _parse_date_from_name(path: Path) -> Optional[str]:
    # Try YYYY-MM-DD anywhere in path
    m = re.search(r'(20\d{2}-\d{2}-\d{2})', path.as_posix())
    if m:
        return m.group(1)
    # Try compact YYYYMMDD in filename
    m2 = re.search(r'(20\d{2})(\d{2})(\d{2})', path.name)
    if m2:
        y, mo, d = m2.groups()
        return f"{y}-{mo}-{d}"
    return None


def _pair_files_by_date(manifest_path: Path) -> Dict[str, Dict[str, Dict[str, Path]]]:
    """Return dict[period][date]['VV'|'VH'] = Path using CSV with filename fallback."""
    pairs: Dict[str, Dict[str, Dict[str, Path]]] = {}
    with manifest_path.open() as f:
        r = csv.DictReader(f)
        for row in r:
            fn = Path(row['filename'])
            pol_csv = (row.get('polarization') or '').upper()
            date_csv = (row.get('date') or '')
            period = row.get('period', 'unknown') or 'unknown'

            pol = pol_csv if pol_csv in ('VV', 'VH') else (_parse_pol_from_name(fn) or '')
            date = date_csv if date_csv else (_parse_date_from_name(fn) or '')
            if pol not in ('VV', 'VH') or not date:
                continue
            pairs.setdefault(period, {}).setdefault(date, {})[pol] = fn
    return pairs


def _pair_all_dates(manifest_path: Path) -> Dict[str, Dict[str, Path]]:
    """Return dict[date]['VV'|'VH'] = Path across all periods (ignore period)."""
    pairs: Dict[str, Dict[str, Path]] = {}
    with manifest_path.open() as f:
        r = csv.DictReader(f)
        for row in r:
            fn = Path(row['filename'])
            pol_csv = (row.get('polarization') or '').upper()
            date_csv = (row.get('date') or '')

            pol = pol_csv if pol_csv in ('VV', 'VH') else (_parse_pol_from_name(fn) or '')
            date = date_csv if date_csv else (_parse_date_from_name(fn) or '')
            if pol not in ('VV', 'VH') or not date:
                continue
            pairs.setdefault(date, {})[pol] = fn
    return pairs

def _find_two_periods(pairs: Dict[str, Dict[str, Dict[str, Path]]], pre_name: str, post_name: str) -> Tuple[Optional[Tuple[str, Dict[str, Path]]], Optional[Tuple[str, Dict[str, Path]]]]:
    def pick_first(period: str):
        if period not in pairs:
            return None
        for d, bands in sorted(pairs[period].items()):
            if 'VV' in bands and 'VH' in bands:
                return d, bands
        return None
    return pick_first(pre_name), pick_first(post_name)


@click.command()
@click.option('--manifest', type=click.Path(exists=True), required=True, help='Path to manifest.csv')
@click.option('--output-dir', type=click.Path(), default='outputs', show_default=True)
@click.option('--pre', default='pre', show_default=True, help='Name of pre period')
@click.option('--post', default='recent', show_default=True, help='Name of post period')
@click.option('--make-plots', is_flag=True, help='Generate PNG comparison figure')
@click.option('--any-period', is_flag=True, help='Auto-pair two most recent dates with VV/VH regardless of period')
def main(manifest: str, output_dir: str, pre: str, post: str, make_plots: bool, any_period: bool) -> None:  # type: ignore[override]
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    mpath = Path(manifest)

    if any_period:
        # Ignore periods: pick two most recent dates with both VV and VH
        all_pairs = _pair_all_dates(mpath)
        # Sort ISO dates descending
        dates_sorted = sorted(all_pairs.keys(), reverse=True)
        sel_dates: List[str] = []
        for d in dates_sorted:
            if 'VV' in all_pairs[d] and 'VH' in all_pairs[d]:
                sel_dates.append(d)
            if len(sel_dates) == 2:
                break
        if len(sel_dates) < 2:
            print('Could not find two dates with complete VV/VH across manifest.')
            return
        pre_date, post_date = sel_dates[1], sel_dates[0]  # older as pre, newer as post
        pre_bands = all_pairs[pre_date]
        post_bands = all_pairs[post_date]
        pre_label, post_label = pre_date, post_date
    else:
        pairs = _pair_files_by_date(mpath)
        pre_sel, post_sel = _find_two_periods(pairs, pre, post)
        if not pre_sel or not post_sel:
            print('Could not find complete VV/VH pairs for given periods.')
            return
        pre_date, pre_bands = pre_sel
        post_date, post_bands = post_sel
        pre_label, post_label = pre, post

    ratio_pre = outdir / f'ratio_{pre_label}_{pre_date}.tif'
    ratio_post = outdir / f'ratio_{post_label}_{post_date}.tif'
    delta = outdir / f'ratio_delta_{pre_label}_to_{post_label}.tif'

    compute_vh_vv_ratio(pre_bands['VV'], pre_bands['VH'], ratio_pre)
    compute_vh_vv_ratio(post_bands['VV'], post_bands['VH'], ratio_post)
    stats = compute_change(ratio_pre, ratio_post, delta)
    print('Delta stats:', stats)

    if make_plots:
        plot_comparison(ratio_pre, ratio_post, delta, outdir / f'ratio_compare_{pre_label}_vs_{post_label}.png')


if __name__ == '__main__':
    main()
