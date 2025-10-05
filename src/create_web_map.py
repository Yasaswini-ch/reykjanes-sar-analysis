"""
Create interactive folium maps for SAR products with NASA-style enhancements.

Usage:
  python src/create_web_map.py --mode single --layers outputs/ratio_recent_*.tif --out outputs/map.html
  python src/create_web_map.py --mode dual --layers outputs/ratio_pre_*.tif outputs/ratio_recent_*.tif --out outputs/dual.html
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import io
import base64
import click
import numpy as np
import rasterio as rio
from rasterio.warp import transform_bounds
from PIL import Image
import folium
from folium.plugins import DualMap, MiniMap, Fullscreen, MousePosition, Timeline, TimelineSlider
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from config import MAP_CENTER


# Known eruption data for Reykjanes Peninsula 2024-2025
ERUPTIONS = [
    {"date": "2024-01-14", "name": "Grindavík", "lat": 63.88, "lon": -22.45, "volume": "~0.01 km³"},
    {"date": "2024-02-08", "name": "Sundhnúkur", "lat": 63.89, "lon": -22.43, "volume": "~0.008 km³"},
    {"date": "2024-03-16", "name": "Sundhnúkur", "lat": 63.89, "lon": -22.42, "volume": "~0.01 km³"},
    {"date": "2024-05-29", "name": "Sundhnúkur", "lat": 63.89, "lon": -22.41, "volume": "~0.005 km³"},
    {"date": "2024-08-22", "name": "Sundhnúkur", "lat": 63.89, "lon": -22.40, "volume": "~0.006 km³"},
    {"date": "2024-11-20", "name": "Sundhnúkur", "lat": 63.88, "lon": -22.41, "volume": "~0.004 km³"},
]


# NASA-inspired colormap for SAR data
def create_nasa_colormap(cmap_type='ratio'):
    """Create NASA-style colormaps for different data types."""
    if cmap_type == 'ratio':
        colors = ['#004d00', '#00b300', '#80ff00', '#ffff00', '#ff9900', '#ff6600']
        return LinearSegmentedColormap.from_list('nasa_ratio', colors)
    elif cmap_type == 'change':
        colors = ['#0066cc', '#66b3ff', '#e6f2ff', '#ffe6e6', '#ff6666', '#cc0000']
        return LinearSegmentedColormap.from_list('nasa_change', colors)
    else:
        return 'viridis'


def geotiff_to_png_data(path: Path, vmin=None, vmax=None, cmap='viridis', 
                        enhance=True) -> Tuple[str, list]:
    """Convert GeoTIFF to base64 PNG with optional NASA-style enhancement."""
    with rio.open(path) as ds:
        arr = ds.read(1)
        bounds = transform_bounds(ds.crs, 'EPSG:4326', *ds.bounds)
    
    arr = np.ma.masked_invalid(arr)
    if hasattr(ds, 'nodata') and ds.nodata is not None:
        arr = np.ma.masked_where(arr == ds.nodata, arr)
    
    if vmin is None:
        vmin = float(np.nanpercentile(arr.compressed(), 2))
    if vmax is None:
        vmax = float(np.nanpercentile(arr.compressed(), 98))
    
    if enhance and isinstance(cmap, str):
        path_str = str(path).lower()
        if 'change' in path_str or 'delta' in path_str:
            cmap = create_nasa_colormap('change')
        elif 'ratio' in path_str or 'vh_vv' in path_str:
            cmap = create_nasa_colormap('ratio')
        else:
            cmap = plt.cm.get_cmap(cmap)
    
    arr_norm = np.clip((arr - vmin) / (vmax - vmin + 1e-6), 0, 1)
    
    if hasattr(cmap, '__call__'):
        rgba = cmap(arr_norm)
        rgb = (rgba[:, :, :3] * 255).astype('uint8')
    else:
        rgb = (arr_norm * 255).astype('uint8')
        rgb = np.stack([rgb, rgb, rgb], axis=-1)
    
    bio = io.BytesIO()
    Image.fromarray(rgb).save(bio, format='PNG')
    data = base64.b64encode(bio.getvalue()).decode('utf-8')
    
    return data, [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]


def add_geotiff_layer(m: folium.Map, tif: Path, name: str, opacity: float = 0.7,
                     vmin=None, vmax=None, cmap='viridis') -> None:
    """Add GeoTIFF as image overlay with NASA-style rendering."""
    data, bounds = geotiff_to_png_data(tif, vmin=vmin, vmax=vmax, cmap=cmap)
    overlay = folium.raster_layers.ImageOverlay(
        image='data:image/png;base64,' + data,
        bounds=bounds,
        name=name,
        opacity=opacity,
        interactive=True,
        cross_origin=False,
    )
    overlay.add_to(m)


def add_eruption_markers(m: folium.Map) -> None:
    """Add markers for known eruption locations with timeline info."""
    for eruption in ERUPTIONS:
        # Create popup content
        popup_html = f"""
        <div style="font-family: 'Courier New', monospace; min-width: 200px;">
            <h4 style="color: #ff6600; margin: 5px 0; border-bottom: 2px solid #ff6600;">
                ERUPTION EVENT
            </h4>
            <table style="width: 100%; font-size: 12px;">
                <tr>
                    <td style="color: #666;"><strong>Date:</strong></td>
                    <td>{eruption['date']}</td>
                </tr>
                <tr>
                    <td style="color: #666;"><strong>Location:</strong></td>
                    <td>{eruption['name']}</td>
                </tr>
                <tr>
                    <td style="color: #666;"><strong>Volume:</strong></td>
                    <td>{eruption['volume']}</td>
                </tr>
            </table>
            <p style="font-size: 10px; color: #999; margin-top: 10px;">
                Source: Icelandic Met Office
            </p>
        </div>
        """
        
        # Add large, bright marker
        folium.CircleMarker(
            location=[eruption['lat'], eruption['lon']],
            radius=15,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"🔥 {eruption['name']} - {eruption['date']}",
            color='#ffff00',
            fill=True,
            fillColor='#ff0000',
            fillOpacity=0.9,
            weight=3
        ).add_to(m)


def add_timeline_panel(m: folium.Map) -> None:
    """Add timeline panel showing eruption chronology."""
    timeline_html = '''
    <div style="position: fixed; 
                bottom: 60px; left: 60px; right: 60px;
                background: linear-gradient(135deg, #0B3D91 0%, #1e5a9e 100%);
                border: 2px solid #00d4ff;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
                z-index: 9999; 
                padding: 15px;
                font-family: 'Courier New', monospace;
                color: white;">
        <div style="border-bottom: 2px solid #00d4ff; padding-bottom: 5px; margin-bottom: 10px;">
            <strong style="color: #00d4ff; text-transform: uppercase; letter-spacing: 1px;">
                ERUPTION TIMELINE 2024-2025
            </strong>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px;">
            <div style="text-align: center; flex: 1;">
                <div style="color: #ff6600; font-weight: bold;">JAN 14</div>
                <div style="color: #aaa; font-size: 9px;">Grindavík</div>
            </div>
            <div style="color: #00d4ff;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="color: #ff6600; font-weight: bold;">FEB 8</div>
                <div style="color: #aaa; font-size: 9px;">Sundhnúkur</div>
            </div>
            <div style="color: #00d4ff;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="color: #ff6600; font-weight: bold;">MAR 16</div>
                <div style="color: #aaa; font-size: 9px;">Sundhnúkur</div>
            </div>
            <div style="color: #00d4ff;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="color: #ff6600; font-weight: bold;">MAY 29</div>
                <div style="color: #aaa; font-size: 9px;">Sundhnúkur</div>
            </div>
            <div style="color: #00d4ff;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="color: #ff6600; font-weight: bold;">AUG 22</div>
                <div style="color: #aaa; font-size: 9px;">Sundhnúkur</div>
            </div>
            <div style="color: #00d4ff;">→</div>
            <div style="text-align: center; flex: 1;">
                <div style="color: #ff6600; font-weight: bold;">NOV 20</div>
                <div style="color: #aaa; font-size: 9px;">Sundhnúkur</div>
            </div>
        </div>
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #00d4ff; 
                    font-size: 10px; color: #aaa; text-align: center;">
            Click red markers on map for detailed eruption information
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(timeline_html))


def add_nasa_styling(m: folium.Map, title: str = "Reykjanes Peninsula SAR Analysis") -> None:
    """Add NASA-style title card and styling to map."""
    
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 60px; 
                width: 500px; 
                background: linear-gradient(135deg, #0B3D91 0%, #1e5a9e 100%);
                border: 2px solid #00d4ff;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
                z-index: 9999; 
                padding: 15px;
                font-family: 'Courier New', monospace;
                color: white;">
        <div style="border-bottom: 2px solid #00d4ff; padding-bottom: 8px; margin-bottom: 10px;">
            <h3 style="margin: 0; color: #00d4ff; text-transform: uppercase; 
                       letter-spacing: 2px; font-size: 16px;">
                🛰️ {title}
            </h3>
        </div>
        <div style="font-size: 12px; line-height: 1.6;">
            <div style="margin-bottom: 8px;">
                <strong style="color: #00d4ff;">MISSION:</strong> 
                <span style="color: #e0e0e0;">Sentinel-1 SAR Change Detection</span>
            </div>
            <div style="margin-bottom: 8px;">
                <strong style="color: #00d4ff;">TARGET:</strong> 
                <span style="color: #e0e0e0;">Reykjanes Peninsula, Iceland</span>
            </div>
            <div style="margin-bottom: 8px;">
                <strong style="color: #00d4ff;">SENSOR:</strong> 
                <span style="color: #e0e0e0;">C-Band SAR (VV/VH Polarization)</span>
            </div>
            <div style="margin-bottom: 8px;">
                <strong style="color: #00d4ff;">PERIOD:</strong> 
                <span style="color: #e0e0e0;">May 2024 - September 2025</span>
            </div>
            <div style="margin-bottom: 8px; padding: 8px; 
                        background: rgba(0, 212, 255, 0.1); 
                        border-left: 3px solid #00d4ff; 
                        border-radius: 3px;">
                <strong style="color: #ffcc00;">LEGEND:</strong><br>
                <span style="color: #00ff00;">🟢 Green</span> → Vegetation/Rough Terrain<br>
                <span style="color: #ffff00;">🟡 Yellow</span> → Smooth Surfaces/Water<br>
                <span style="color: #ff0000;">🔴 Red</span> → Increased Roughness<br>
                <span style="color: #0066ff;">🔵 Blue</span> → Decreased Roughness
            </div>
            <div style="font-size: 10px; color: #888; text-align: right; margin-top: 8px;">
                DATA: ESA Copernicus | PROCESSING: ASF HyP3
            </div>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    footer_html = '''
    <div style="position: fixed; 
                bottom: 10px; left: 60px; 
                background: rgba(11, 61, 145, 0.9);
                border: 1px solid #00d4ff;
                border-radius: 5px;
                padding: 8px 15px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: #00d4ff;
                z-index: 9999;">
        <strong>NASA SPACE APPS 2025</strong> | Volcanic Monitoring Through SAR
    </div>
    '''
    m.get_root().html.add_child(folium.Element(footer_html))


def add_coordinate_display(m: folium.Map) -> None:
    """Add mouse position display with NASA-style formatting."""
    formatter = "function(num) {return L.Util.formatNum(num, 5) + ' º ';};"
    MousePosition(
        position='bottomright',
        separator=' | ',
        empty_string='Move cursor to see coordinates',
        lng_first=True,
        num_digits=20,
        prefix='<strong style="color: #00d4ff;">COORDS:</strong> ',
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(m)


@click.command()
@click.option('--mode', type=click.Choice(['single','dual']), required=True,
              help='Map mode: single (layers) or dual (side-by-side)')
@click.option('--layers', multiple=True, type=click.Path(exists=True), 
              help='GeoTIFF paths; for dual, provide exactly two')
@click.option('--out', type=click.Path(), required=True,
              help='Output HTML file path')
@click.option('--zoom', type=int, default=10,
              help='Initial zoom level')
@click.option('--basemap', default='CartoDB dark_matter', show_default=True,
              help='Base map tile layer')
@click.option('--title', default='Reykjanes Peninsula SAR Analysis',
              help='Map title')
@click.option('--vmin', type=float, default=None,
              help='Minimum value for colormap scaling')
@click.option('--vmax', type=float, default=None,
              help='Maximum value for colormap scaling')
@click.option('--add-eruptions/--no-eruptions', default=True,
              help='Add eruption markers and timeline')
def main(mode: str, layers: List[str], out: str, zoom: int, 
         basemap: str, title: str, vmin: float, vmax: float, add_eruptions: bool) -> None:
    """Create NASA-style interactive SAR maps with eruption markers and timeline."""
    
    print(f"🛰️  Creating {mode} mode map with NASA styling...")
    
    if mode == 'single':
        m = folium.Map(
            location=MAP_CENTER, 
            zoom_start=zoom, 
            tiles=basemap,
            control_scale=True
        )
        
        if not layers:
            folium.Marker(MAP_CENTER, tooltip='No layers provided').add_to(m)
            print("⚠️  No layers provided, creating empty map")
        else:
            for i, p in enumerate(layers):
                layer_path = Path(p)
                layer_name = layer_path.stem.replace('_', ' ').title()
                
                if 'change' in str(p).lower() or 'delta' in str(p).lower():
                    cmap = create_nasa_colormap('change')
                    default_vmin = vmin if vmin is not None else -3
                    default_vmax = vmax if vmax is not None else 3
                elif 'ratio' in str(p).lower():
                    cmap = create_nasa_colormap('ratio')
                    default_vmin = vmin if vmin is not None else -25
                    default_vmax = vmax if vmax is not None else -5
                else:
                    cmap = 'viridis'
                    default_vmin = vmin
                    default_vmax = vmax
                
                add_geotiff_layer(m, layer_path, layer_name, opacity=0.7,
                                vmin=default_vmin, vmax=default_vmax, cmap=cmap)
                print(f"  ✓ Added layer: {layer_name}")
        
        # Add eruption markers and timeline
        if add_eruptions:
            add_eruption_markers(m)
            add_timeline_panel(m)
            print("  ✓ Added eruption markers and timeline")
        
        # Add NASA styling and controls
        add_nasa_styling(m, title)
        add_coordinate_display(m)
        Fullscreen(position='topright').add_to(m)
        MiniMap(toggle_display=True, position='topright').add_to(m)
        folium.LayerControl(position='topright', collapsed=False).add_to(m)
        
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        m.save(out)
        print(f'✅ Saved map to {out}')
        
    else:  # dual mode
        if len(layers) != 2:
            raise click.UsageError('Dual mode requires exactly two layers')
        
        dm = DualMap(
            location=MAP_CENTER, 
            zoom_start=zoom,
            tiles_layer1=basemap,
            tiles_layer2=basemap
        )
        
        left_path = Path(layers[0])
        left_name = left_path.stem.replace('_', ' ').title()
        add_geotiff_layer(dm.m1, left_path, left_name, 
                         vmin=vmin or -25, vmax=vmax or -5,
                         cmap=create_nasa_colormap('ratio'))
        
        right_path = Path(layers[1])
        right_name = right_path.stem.replace('_', ' ').title()
        add_geotiff_layer(dm.m2, right_path, right_name,
                         vmin=vmin or -25, vmax=vmax or -5,
                         cmap=create_nasa_colormap('ratio'))
        
        # Add eruption markers to both maps
        if add_eruptions:
            add_eruption_markers(dm.m1)
            add_eruption_markers(dm.m2)
            add_timeline_panel(dm.m1)
            print("  ✓ Added eruption markers to both panels")
        
        for m in [dm.m1, dm.m2]:
            Fullscreen(position='topright').add_to(m)
            folium.LayerControl(position='topright').add_to(m)
        
        add_nasa_styling(dm.m1, f"{title} - Comparison View")
        
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        dm.save(out)
        print(f'✅ Saved dual map to {out}')
        print(f'   Left: {left_name}')
        print(f'   Right: {right_name}')


if __name__ == '__main__':
    main()