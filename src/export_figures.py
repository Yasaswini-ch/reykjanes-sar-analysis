"""
Export publication-quality figures for analysis products.

Usage:
  python src/export_figures.py --manifest data/rtc/manifest.csv --outdir outputs/figures
"""
from __future__ import annotations
from pathlib import Path
import io
import click
import numpy as np
import pandas as pd
import rasterio as rio
import matplotlib.pyplot as plt

from analyze_backscatter import compute_vh_vv_ratio, compute_change, _read_band as _read  # type: ignore


def _hist(ax, arr: np.ndarray, title: str) -> None:
    vals = arr[np.isfinite(arr)]
    if vals.size:
        ax.hist(vals, bins=60, color='#444', alpha=0.9)
    ax.set_title(title)


def create_overview_figure(vv_tif: Path, vh_tif: Path, ratio_tif: Path, output_png: Path) -> None:
    vv, _ = _read(vv_tif)
    vh, _ = _read(vh_tif)
    ratio, _ = _read(ratio_tif)

    fig = plt.figure(figsize=(12, 8), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)

    ax1 = fig.add_subplot(gs[0, 0]); im1 = ax1.imshow(vv, cmap='gray'); ax1.set_title('VV'); ax1.axis('off'); fig.colorbar(im1, ax=ax1, shrink=0.7)
    ax2 = fig.add_subplot(gs[0, 1]); im2 = ax2.imshow(vh, cmap='gray'); ax2.set_title('VH'); ax2.axis('off'); fig.colorbar(im2, ax=ax2, shrink=0.7)
    ax3 = fig.add_subplot(gs[0, 2]); im3 = ax3.imshow(ratio, cmap='RdYlGn'); ax3.set_title('VH/VV (dB)'); ax3.axis('off'); fig.colorbar(im3, ax=ax3, shrink=0.7)

    _hist(fig.add_subplot(gs[1, 0]), vv, 'VV histogram')
    _hist(fig.add_subplot(gs[1, 1]), vh, 'VH histogram')
    _hist(fig.add_subplot(gs[1, 2]), ratio, 'VH/VV (dB) hist')

    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=200)
    plt.close(fig)


def create_timeseries_plot(manifest_csv: Path, output_png: Path) -> None:
    df = pd.read_csv(manifest_csv)
    # Compute mean ratio per date when both VV and VH are present: this is a placeholder aggregation
    # In practice, use precomputed ratio rasters. Here we just count available VV/VH as proxy.
    dates = sorted(set(df['date']))
    means = np.arange(len(dates), dtype=float)  # simple placeholder ramp
    stds = np.ones_like(means) * 0.5

    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    ax.errorbar(dates, means, yerr=stds, fmt='-o', color='tab:blue')
    for d in ['2024-11-10','2024-12-18','2025-01-14']:
        ax.axvline(d, color='r', linestyle='--', alpha=0.5)
    ax.set_title('Mean VH/VV ratio over time (illustrative)')
    ax.set_xlabel('Date'); ax.set_ylabel('dB')
    ax.tick_params(axis='x', rotation=45)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=200)
    plt.close(fig)


@click.command()
@click.option('--manifest', type=click.Path(exists=True), default='data/rtc/manifest.csv', show_default=True)
@click.option('--outdir', type=click.Path(), default='outputs/figures', show_default=True)
def main(manifest: str, outdir: str) -> None:
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    man = Path(manifest)

    # Attempt to find one VV/VH pair to build overview
    if man.exists():
        df = pd.read_csv(man)
        # Pick any period with VV and VH
        for period in ['pre','during','recent']:
            sub = df[(df['period']==period) & df['polarization'].isin(['VV','VH'])]
            if not sub.empty and sub['polarization'].nunique() == 2:
                try:
                    vv_path = Path(sub[sub['polarization']=='VV']['filename'].iloc[0])
                    vh_path = Path(sub[sub['polarization']=='VH']['filename'].iloc[0])
                    ratio_path = out / f'ratio_{period}.tif'
                    compute_vh_vv_ratio(vv_path, vh_path, ratio_path)
                    create_overview_figure(vv_path, vh_path, ratio_path, out / f'overview_{period}.png')
                    break
                except Exception as e:
                    print('Overview figure failed:', e)

    # Time series plot (illustrative)
    try:
        create_timeseries_plot(man, out / 'timeseries_ratio.png')
    except Exception as e:
        print('Timeseries figure failed:', e)


if __name__ == '__main__':
    main()
