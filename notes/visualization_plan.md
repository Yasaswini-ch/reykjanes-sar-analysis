# Visualization Plan

This document specifies all figures to produce, including layout, dimensions, styles, colormaps, and annotations. Use this as a blueprint when generating outputs under `outputs/` and `outputs/figures/`.

## Figure 1: Study Area Overview Map
- **Purpose**: Provide geographic context of Reykjanes Peninsula and key sites (vents, lava fields, towns, roads).
- **Data Layers**:
  - Base: OpenStreetMap or Natural Earth via folium or contextily.
  - AOI: `aoi.geojson` outline, styled with thick semi-transparent boundary.
  - Optional overlays: recent Sentinel-2 true-color for context (if cloud-free day available).
- **Dimensions**: 1920x1080 px (landscape), 300 dpi for print export.
- **Projection**: Web Mercator for web; include EPSG code in caption.
- **Symbology**:
  - AOI outline: hex #FF6B6B, 2–3 px.
  - Towns/labels: contrasting color (e.g., #2E86AB) and halo for legibility.
  - Scale bar and north arrow for static export.
- **Annotations**:
  - Key volcano/eruptive fissures labelled.
  - Major roads, towns (Grindavík, Keflavík, etc.).
  - Coordinates grid optional (0.25° spacing) for print.
- **Output**:
  - Static PNG: `outputs/figures/overview_map.png`.
  - Optional interactive HTML: `outputs/volcano_map.html`.

## Figure 2: Multi-Polarization Comparison (VV / VH / Ratio)
- **Purpose**: Show spatial patterns across VV, VH, and VH/VV ratio for one representative date or mosaic.
- **Input**: HyP3 RTC GeoTIFFs (Gamma0), resampled to common grid.
- **Panels**: 3 side-by-side panels (VV, VH, Ratio).
- **Dimensions**: 2400x900 px (3 panels at 800x900 each), 300 dpi.
- **Colormaps**:
  - VV (dB): grayscale or `viridis` clipped to, e.g., [-20, 0] dB.
  - VH (dB): `magma` or `inferno` clipped to [-27, -5] dB.
  - Ratio (VH/VV in dB): diverging, e.g., `RdBu` or `coolwarm`, centered at 0 dB, range [-10, +10] dB.
- **Normalization**: Percentile stretch (2–98%) per panel with consistent legend text.
- **Annotations**:
  - AOI boundary overlay.
  - Colorbars with units and ranges.
  - Captions: acquisition date/time, orbit, incidence angle (if available).
  - Insets: 1–2 zoom boxes for key features.
- **Output**:
  - PNG: `outputs/figures/vv_vh_ratio_tripanel.png`.

## Figure 3: Change Detection (Pre / Post / Delta)
- **Purpose**: Show change in backscatter due to eruptive activity or lava emplacement.
- **Input**: Pre- and Post-event VV and VH images, co-registered.
- **Panels**:
  - Pre ratio (VH/VV in dB), Post ratio, Delta (Post - Pre in dB).
- **Dimensions**: 2400x900 px, 300 dpi.
- **Colormaps**:
  - Pre/Post ratio: `RdBu` centered at 0 dB, range [-10, +10] dB.
  - Delta: diverging `PuOr` or `BrBG`, range [-6, +6] dB (tunable after inspection).
- **Annotations**:
  - AOI overlay, scalebar, north arrow (for static).
  - Histogram insets for Delta distribution with mean/median/std labeled.
  - Text callouts for notable positive/negative changes.
- **Output**:
  - PNG: `outputs/figures/ratio_change_tripanel.png`.

## Figure 4: Interactive Web Map Specification
- **Purpose**: Allow exploration of layers and toggling between products.
- **Framework**: folium/Leaflet via `src/create_web_map.py` and `src/folium_map.py`.
- **Layers**:
  - Basemap (OSM), AOI, VV, VH, Ratio, Delta Ratio.
  - Optional: Coherence (if InSAR processed), Optical (Sentinel-2 true-color).
- **UI Elements**:
  - Layer control with grouped overlays.
  - Opacity sliders for each raster layer.
  - Mouse position lat/lon readout.
  - Legend popups with value ranges/units.
- **Performance**:
  - Pre-generate Cloud-Optimized GeoTIFFs (COGs) or tiles for large rasters.
- **Output**:
  - HTML: `outputs/map.html` (and `outputs/dual.html` if dual-view is enabled).

## Figure 5: Hypothesis Diagram (Sketch Description)
- **Purpose**: Communicate expected scattering behaviors and changes.
- **Elements**:
  - Cartoon panels showing lava roughness vs moisture effects on VV/VH.
  - Vegetation vs bare rock scattering schematics (surface vs volume scatter).
  - Temporal axis showing expected coherence loss during/after eruption.
  - Water bodies with specular returns (low backscatter) and surrounding damp soils.
- **Dimensions**: 1600x900 px, vector-friendly if possible (SVG for source, PNG for export).
- **Annotations**:
  - Clear labels for physical processes.
  - Legends describing polarization response.
- **Output**:
  - PNG: `outputs/figures/hypothesis_diagram.png` (source: `notes/sketches/hypothesis_diagram.svg`).

## Common Styling Guidance
- **Fonts**: Sans-serif (e.g., DejaVu Sans) for consistency with matplotlib defaults.
- **Linework**: AOI/annotation lines 2–3 px, semi-transparent fills for insets.
- **Colorbars**: Include units (dB) and tick labels with reasonable spacing.
- **Reproducibility**: Save matplotlib scripts and random seeds; record color limits used.
