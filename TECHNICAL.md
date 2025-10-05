# Technical Documentation

This document provides installation steps, command-line usage, the data processing pipeline, and code documentation for the "Through the Radar Looking Glass" project.

---

## 1) Installation

- **Prerequisites**
  - Python 3.9+ (recommended)
  - A modern web browser (for viewing the interactive HTML map)
  - Optional (for data access/processing): NASA Earthdata Login

- **Clone and set up a virtual environment (Windows PowerShell)**
  ```powershell
  git clone <your-repo-url>.git
  cd windsorf-project
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

- **NASA Earthdata credentials (if using ASF services)**
  1. Create an account: https://urs.earthdata.nasa.gov/
  2. Ensure access to ASF DAAC applications: https://asf.alaska.edu/
  3. For programmatic access using `asf-search`/`hyp3-sdk`, you will authenticate via browser or environment variables when prompted.

- **Optional: Vercel CLI for hosting outputs/**
  ```powershell
  npm i -g vercel
  ```

---

## 2) Command-line Usage

The repository currently includes a simple visualization script and static outputs. Typical tasks:

- **Generate a quick VH/VV ratio visualization from a GeoTIFF**
  - Script: `demo.py`
  - Input: `outputs/ratio_post_nov2024.tif`
  - Output: `outputs/ratio_map_display.png`
  ```powershell
  # From project root
  .\.venv\Scripts\Activate.ps1
  python demo.py
  ```

- **Open the interactive web map locally**
  - Primary file: `outputs/nasa_map_complete.html`
  ```powershell
  # On Windows
  start .\outputs\nasa_map_complete.html
  ```

- **Deploy the static map (optional)**
  ```powershell
  cd outputs
  vercel --prod --yes --confirm
  ```

> Note: If your entry file is not `index.html`, you may duplicate it for static hosts:
```powershell
Copy-Item .\outputs\nasa_map_complete.html .\outputs\index.html
```

---

## 3) Data Processing Pipeline (Overview)

The project focuses on using Sentinel‑1 SAR to classify surfaces and detect change in Iceland’s Reykjanes Peninsula. Processing is performed primarily via ASF HyP3 (cloud) and Python analysis locally.

1. **Define Area of Interest (AOI)**
   - File: `aoi.geojson` (Polygon over Reykjanes Peninsula)

2. **Scene Discovery (ASF Search API)**
   - Use `asf-search` to find Sentinel‑1 scenes matching AOI, date range, and acquisition mode (e.g., IW, GRD/SLC as applicable).
   - Reference: https://docs.asf.alaska.edu/api/

3. **Cloud Processing (ASF HyP3)**
   - Submit jobs to HyP3 for RTC (Radiometric Terrain Correction) and produce analysis-ready GeoTIFFs.
   - Reference: https://hyp3-docs.asf.alaska.edu/

4. **Local Analysis (Python)**
   - Compute VH/VV ratios for each time period using `rasterio`/`numpy`.
   - Generate change maps (e.g., difference of ratios or band statistics) across dates.
   - Export products as GeoTIFFs and PNGs to `outputs/`.

5. **Visualization & Storytelling**
   - Assemble an interactive map (`outputs/nasa_map_complete.html`) with layers for different time periods and change overlays.

### Example: Reading a GeoTIFF and plotting a ratio map
```python
import rasterio as rio
import matplotlib.pyplot as plt

with rio.open('outputs/ratio_post_nov2024.tif') as src:
    data = src.read(1)

plt.figure(figsize=(10, 8))
plt.imshow(data, cmap='RdYlGn', vmin=-25, vmax=-5)
plt.colorbar(label='VH/VV Ratio (dB)')
plt.title('Surface Classification via VH/VV Ratio')
plt.axis('off')
plt.tight_layout()
plt.savefig('outputs/ratio_map_display.png', dpi=150)
```

---

## 4) Code Documentation

- **Project Root**
  - `README.md` — Full project narrative, results, screenshots, and links.
  - `requirements.txt` — Python package dependencies.
  - `aoi.geojson` — AOI polygon used for discovery/processing.
  - `demo.py` — Minimal example to render a ratio GeoTIFF as a PNG.
  - `techinal.md` — This technical document.

- **outputs/**
  - `nasa_map_complete.html` — Interactive web map for exploration.
  - `ratio_post_nov2024.tif` — Example ratio GeoTIFF (VH/VV).
  - `ratio_map_display.png` — Rendered visualization from `demo.py`.
  - Additional figures, overlays, and comparison images referenced by `README.md`.

- **notes/** (if present)
  - Project notes, timelines, and resources.

### Key Python Dependencies
- `rasterio`, `numpy`, `pandas`, `matplotlib`, `folium`, `geopandas`, `shapely`, `Pillow`, `asf-search`, `hyp3-sdk`.

### Typical Workflow Commands (Windows)
```powershell
# 1) Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) Run example visualization
python demo.py

# 3) View interactive map
start .\outputs\nasa_map_complete.html
```

---

## 5) Troubleshooting

- **GDAL/PROJ issues on Windows**
  - If `rasterio`/`geopandas` import errors occur, ensure wheels installed from PyPI match Python version. Consider installing `pip install rasterio==1.3.*` first, then others.

- **Earthdata authentication**
  - When using `asf-search`/`hyp3-sdk`, ensure your browser completes login; if scripts run non-interactively, consult each library’s docs for token or `.netrc` usage.

- **Large files**
  - Keep large rasters in `outputs/` and avoid committing them if your repository must remain lightweight.

---

## 6) License & Attribution

- Code licensed under MIT (see `README.md`).
- Data credits: ESA/Copernicus Sentinel‑1; Processing courtesy of ASF HyP3 (NASA EOSDIS/ASF).
- Basemap credits: OpenStreetMap contributors (if used in interactive map).
