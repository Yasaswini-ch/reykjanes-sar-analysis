# InSAR Processing Notes (Sentinel-1 SLC)

This repo focuses on GRD multi-pol analysis and interactive maps. For InSAR pairs and optional time series, use:

## ESA SNAP (GPT) pairwise workflow
- Apply-Orbit-File (master, slave)
- TOPS Split (IW), Subset (AOI), Deburst
- Back-Geocoding (coregistration)
- Interferogram Formation + Coherence
- Goldstein Filter
- Phase Unwrapping (SNAPHU external) – optional for hackathon
- Terrain Correction (Range-Doppler) → GeoTIFF for coherence and wrapped phase

Tips:
- Keep temporal/perpendicular baselines short (e.g., <24 days if possible; check availability after Sentinel-1B outage).
- Use Copernicus 30 m DEM. Ensure orbit files are up to date.

## ISCE2/ARIA + MintPy (time series)
- Process SLC stack to interferograms (ARIA-tools/ISCE2)
- MintPy steps: prep_isce.py → smallbaselineApp.py → view.py
- Outputs: velocity, cumulative displacement, coherence time series.

## References
- SNAP tutorials: https://step.esa.int/main/doc/tutorials/
- MintPy docs: https://mintpy.readthedocs.io/
