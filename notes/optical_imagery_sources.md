# Optical Imagery Sources for Validation

Use the following sources to obtain optical imagery for visual validation and context. Align optical acquisition dates with SAR dates when possible to compare surface conditions.

## Sentinel Hub EO Browser
- **URL**: https://apps.sentinel-hub.com/eo-browser/
- **Steps**:
  1. Search for "Reykjanes Peninsula, Iceland" or paste coordinates near the AOI center (e.g., 63.95, -22.35).
  2. Choose a collection: "Sentinel-2 L2A" (surface reflectance, atmospheric corrected).
  3. Set the **Time range** to match key SAR dates (see below). Use the cloud filter slider to <20% initially.
  4. Select a visualization: "True color" (RGB), or "NDVI" for vegetation context.
  5. Use the **Compare** tool to set pre/post dates and swipe between them.
  6. Click **Download** to export as PNG/JPEG/GeoTIFF. For georeferenced overlays, choose GeoTIFF.
- **Recommended Settings**:
  - Cloud coverage: start with <20%, adjust as needed due to Icelandic conditions.
  - Visualization: True-color for context, False-color (SWIR) to highlight lava/wetness if desired.
  - Export: 10 m resolution (native), WGS84 / EPSG:4326 or as provided.

### Suggested Dates (Align with SAR)
Use SAR acquisition windows configured in `src/config.py`. Example placeholders below; replace with actual submission dates:
- Pre-event window: [YYYY-MM-DD] to [YYYY-MM-DD]
- During-event key dates: [YYYY-MM-DD], [YYYY-MM-DD]
- Recent/post-event: [YYYY-MM-DD]

Record the chosen Sentinel-2 dates that best match SAR dates (within ±3 days is often acceptable given weather):
- Pre: [INSERT S2 DATE] vs SAR [INSERT S1 DATE]
- During: [INSERT S2 DATE] vs SAR [INSERT S1 DATE]
- Post: [INSERT S2 DATE] vs SAR [INSERT S1 DATE]

## Google Earth Engine (GEE)
- **URL**: https://code.earthengine.google.com/
- **Collections**:
  - `COPERNICUS/S2_SR_HARMONIZED` (Sentinel-2 L2A)
  - `COPERNICUS/S2_CLOUD_PROBABILITY` for cloud masking
- **Approach**:
  - Filter by AOI and dates to match SAR acquisitions.
  - Use s2cloudless or QA60 to mask clouds; export mosaics to Google Drive as GeoTIFF.
- **Notes**: Requires Google account; scripting with JavaScript or Python API.

## Copernicus Open Access Hub / Data Space
- **URL**: https://dataspace.copernicus.eu/
- **Use Case**: Direct product downloads (SAFE format) for maximum control.
- **Steps**:
  1. Register and log in.
  2. Search by AOI (upload `aoi.geojson`) and date range.
  3. Filter to Sentinel-2 MSI Level-2A.
  4. Download and process locally (e.g., with SNAP) if needed.

## Screenshots and Exports
- **Static Figures**:
  - Use EO Browser's Compare tool and export PNG with labels; save to `outputs/figures/optical_pre_post.png`.
- **Georeferenced Overlays**:
  - Export GeoTIFFs for overlay in the web map (`outputs/map.html`).
- **Documentation**:
  - Record product IDs, acquisition times, and % cloud cover in a small CSV: `data/optical_manifest.csv` for traceability.
