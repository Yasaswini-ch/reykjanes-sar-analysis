"""
Utilities for basic raster statistics and period comparisons.

Usage:
  python src/statistics.py --tif outputs/ratio_pre.tif
  python src/statistics.py --compare outputs/ratio_pre.tif outputs/ratio_recent.tif --out results.csv

Notes:
- Uses simple global stats; optional shapefile mask for zonal stats if provided.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional, Tuple
import click
import numpy as np
import rasterio as rio
import pandas as pd

try:
    import geopandas as gpd  # optional for masking
except Exception:  # pragma: no cover
    gpd = None  # type: ignore


def _read(path: Path) -> Tuple[np.ndarray, dict]:
    with rio.open(path) as ds:
        arr = ds.read(1).astype('float32')
        prof = ds.profile
        nodata = ds.nodata
    if nodata is not None:
        arr = np.where(arr == nodata, np.nan, arr)
    return arr, prof


def get_raster_stats(tif_path: str) -> Dict[str, float]:
    arr, _ = _read(Path(tif_path))
    vals = arr[np.isfinite(arr)]
    if vals.size == 0:
        return {k: float('nan') for k in ['min','max','mean','std','p5','p50','p95']}
    return {
        'min': float(np.nanmin(vals)),
        'max': float(np.nanmax(vals)),
        'mean': float(np.nanmean(vals)),
        'std': float(np.nanstd(vals)),
        'p5': float(np.nanpercentile(vals, 5)),
        'p50': float(np.nanpercentile(vals, 50)),
        'p95': float(np.nanpercentile(vals, 95)),
    }


def compare_periods(pre_tif: str, post_tif: str) -> Dict[str, float]:
    a, _ = _read(Path(pre_tif))
    b, _ = _read(Path(post_tif))
    mask = np.isfinite(a) & np.isfinite(b)
    if not np.any(mask):
        return {'delta_mean': float('nan'), 'delta_std': float('nan')}
    d = (b - a)[mask]
    return {'delta_mean': float(np.nanmean(d)), 'delta_std': float(np.nanstd(d))}


@click.command()
@click.option('--tif', 'single_tif', type=click.Path(exists=True), help='Compute stats for a single raster')
@click.option('--compare', nargs=2, type=click.Path(exists=True), help='Compare two rasters (post - pre)')
@click.option('--out', type=click.Path(), help='Optional CSV output for stats')
def cli(single_tif: Optional[str], compare: Optional[Tuple[str,str]], out: Optional[str]) -> None:
    rows = []
    if single_tif:
        s = get_raster_stats(single_tif)
        s['file'] = single_tif
        rows.append(s)
        print('Stats:', s)
    if compare:
        d = compare_periods(compare[0], compare[1])
        d['pre'] = compare[0]
        d['post'] = compare[1]
        rows.append(d)
        print('Comparison:', d)
    if out and rows:
        df = pd.DataFrame(rows)
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        print('Wrote', out)


if __name__ == '__main__':
    cli()
