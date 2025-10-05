# Quickstart (Windows, HyP3, GRD-only)

- **Prerequisites**
  - Python 3.9+ (recommended 3.11)
  - Earthdata Login account (https://urs.earthdata.nasa.gov/)
  - ~10–20 GB free disk space

- **Install**
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- **Authentication**
Create a `.netrc` in your user home (e.g., `C:\Users\<you>\`):
```
machine urs.earthdata.nasa.gov login <YOUR_USERNAME> password <YOUR_PASSWORD>
```
Then run once (browser):
```
python -c "import asf_search as asf; asf.grant_urs("""https://auth.asf.alaska.edu/""")"
```

- **Configure AOI & Dates**
Adjust `src/config.py` if needed. AOI is `aoi.geojson` (Reykjanes bbox).

- **Workflow (10 Steps)**
1. Submit RTC jobs (limit scenes per period):
   ```
   python src/submit_hyp3_jobs.py --limit 2
   ```
2. Wait ~10–30 minutes for HyP3 jobs to complete.
3. Download and extract results; build manifest:
   ```
   python src/download_hyp3_results.py
   ```
4. Inspect `data/rtc/manifest.csv`.
5. Analyze VH/VV ratio and changes:
   ```
   python src/analyze_backscatter.py --manifest data/rtc/manifest.csv --output-dir outputs --make-plots
   ```
6. Compute statistics:
   ```
   python src/statistics.py --tif outputs/ratio_recent_*.tif --out outputs/stats.csv
   ```
7. Create interactive single map:
   ```
   python src/create_web_map.py --mode single --layers outputs/ratio_compare_pre_vs_recent.tif --out outputs/map.html
   ```
8. Create dual (before/after) map:
   ```
   python src/create_web_map.py --mode dual --layers outputs/ratio_pre_*.tif outputs/ratio_recent_*.tif --out outputs/dual.html
   ```
9. Export publication figures:
   ```
   python src/export_figures.py
   ```
10. Run batch pipeline end-to-end:
   ```
   python src/batch_process.py
   ```

- **Troubleshooting**
- HyP3 auth errors: verify Earthdata login and HyP3 token; re-run step 1 after login.
- Empty search: adjust date ranges in `src/config.py` or remove `ASCENDING` constraint in `src/submit_hyp3_jobs.py`.
- Raster errors: ensure GeoTIFFs exist and manifest paths are valid.

- **Expected Outputs**
- `data/rtc/` HyP3 RTC products (unzipped)
- `data/rtc/manifest.csv` inventory
- `outputs/` ratio GeoTIFFs, comparison PNGs, maps, figures

- **Estimated Times**
- Submit/search: 1–2 min
- HyP3 processing: 10–30+ min per batch
- Downloads and analysis: 5–15 min
