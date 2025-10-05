import io
import base64
import click
import folium
import numpy as np
import rasterio as rio
from rasterio.warp import transform_bounds
from PIL import Image


def add_geotiff_layer(m, path, name, vmin=None, vmax=None, cmap='viridis', opacity=0.8):
    with rio.open(path) as ds:
        arr = ds.read(1)
        bounds = transform_bounds(ds.crs, 'EPSG:4326', *ds.bounds)
    if vmin is None:
        vmin = np.nanpercentile(arr, 2)
    if vmax is None:
        vmax = np.nanpercentile(arr, 98)
    a = np.clip((arr - vmin) / (vmax - vmin + 1e-6), 0, 1)
    png = (a * 255).astype('uint8')
    bio = io.BytesIO()
    Image.fromarray(png).save(bio, format='PNG')
    data = base64.b64encode(bio.getvalue()).decode('utf-8')

    overlay = folium.raster_layers.ImageOverlay(
        image='data:image/png;base64,' + data,
        bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
        name=name, opacity=opacity, interactive=True, cross_origin=False
    )
    overlay.add_to(m)


@click.command()
@click.option('--center', nargs=2, type=float, default=(63.95, -22.35), show_default=True, help='lat lon')
@click.option('--zoom', type=int, default=10)
@click.option('--layers', multiple=True, help='List of GeoTIFF paths to add')
@click.option('--names', multiple=True, help='Optional names for layers (match count)')
@click.option('--out', default='outputs/volcano_map.html', show_default=True)
@click.option('--dual', is_flag=True, help='Generate side-by-side dual map if two layers provided')
@click.option('--basemap', default='CartoDB positron', show_default=True)
def main(center, zoom, layers, names, out, dual, basemap):
    if names and len(names) != len(layers):
        raise click.UsageError('--names count must match --layers count')

    m = folium.Map(location=center, zoom_start=zoom, tiles=basemap)

    if not layers:
        folium.Marker(center, tooltip='No layers provided').add_to(m)
    else:
        for i, path in enumerate(layers):
            name = names[i] if names else f'Layer {i+1}'
            add_geotiff_layer(m, path, name)

    folium.LayerControl().add_to(m)
    out_path = out
    os_dir = out_path.rsplit('/', 1)[0]
    import os
    os.makedirs(os_dir, exist_ok=True)
    m.save(out_path)
    print('Saved map to', out_path)


if __name__ == '__main__':
    main()
