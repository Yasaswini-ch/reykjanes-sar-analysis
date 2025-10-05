"""
Download completed HyP3 RTC products for jobs named 'reykjanes_*', extract, and build a manifest.

Usage:
  python src/download_hyp3_results.py

- Reads job metadata from data/hyp3_jobs.json if present; otherwise queries HyP3 by name pattern.
- Downloads to data/rtc/ and extracts ZIPs.
- Organizes by period (pre/during/recent) using job names.
- Creates data/rtc/manifest.csv with filename, date, polarization, period.
"""
from __future__ import annotations
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import zipfile

from hyp3_sdk import HyP3

from config import OUTPUT_DIRS


def read_jobs_meta(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    try:
        meta = json.loads(path.read_text())
        return meta.get('submitted', [])
    except Exception:
        return []


def safe_extract(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(out_dir)


def guess_period_from_name(name: str) -> str:
    for p in ('pre', 'during', 'recent'):
        if f"_{p}_" in name:
            return p
    return 'unknown'


def build_manifest(rtc_dir: Path, manifest_path: Path) -> None:
    rows = []
    for tif in rtc_dir.rglob('*.tif'):
        # Expect filenames like *_VV.tif or *_VH.tif
        pol = 'VV' if '_VV' in tif.stem.upper() else ('VH' if '_VH' in tif.stem.upper() else '')
        # date guess from path or name
        m = re.search(r'(20\d{2}-\d{2}-\d{2})', tif.as_posix())
        date_str = m.group(1) if m else ''
        period = tif.parent.name if tif.parent.name in ('pre','during','recent') else 'unknown'
        rows.append({'filename': str(tif), 'date': date_str, 'polarization': pol, 'period': period})

    with manifest_path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['filename','date','polarization','period'])
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    data_dir = Path(OUTPUT_DIRS['raw']).parent
    rtc_dir = Path(OUTPUT_DIRS['rtc'])
    rtc_dir.mkdir(parents=True, exist_ok=True)
    jobs_meta_path = data_dir / 'hyp3_jobs.json'

    jobs_meta = read_jobs_meta(jobs_meta_path)

    hyp3 = HyP3()

    # If we have job IDs, query their status; else fall back to name search.
    jobs_to_check = []
    if jobs_meta:
        for j in jobs_meta:
            jobs_to_check.append(j.get('job_id'))
    else:
        print("No local job metadata found; attempting to find jobs by name pattern 'reykjanes_'")

    # Attempt download of completed jobs
    try:
        recent_jobs = hyp3.find_jobs()
    except Exception as e:
        print(f"HyP3 job query failed: {e}", file=sys.stderr)
        return
    
    # Filter jobs by our metadata (job_ids) or by name prefix if no metadata
    if jobs_to_check:
        job_id_set = {jid for jid in jobs_to_check if jid}
        found = [j for j in recent_jobs if getattr(j, 'job_id', None) in job_id_set]
    else:
        found = [j for j in recent_jobs if getattr(j, 'name', '') and getattr(j, 'name').startswith('reykjanes_')]

    # Select completed jobs only
    completed = [j for j in found if getattr(j, 'status_code', '').lower() == 'succeeded' or getattr(j, 'status', '').lower() == 'succeeded']
    if not completed:
        print('No completed jobs yet. Try again later.')
        return

    for job in completed:
        try:
            # Download to rtc_dir root
            job.download_files(rtc_dir)
        except Exception as e:
            print(f"Download failed for {getattr(job, 'name', 'job')}: {e}", file=sys.stderr)

    # Extract ZIPs and organize by period
    for z in rtc_dir.glob('*.zip'):
        period = guess_period_from_name(z.stem)
        target = rtc_dir / period
        target.mkdir(exist_ok=True)
        try:
            safe_extract(z, target)
            z.unlink(missing_ok=True)
        except Exception as e:
            print(f"Extract failed {z.name}: {e}", file=sys.stderr)

    # Build manifest
    manifest_path = rtc_dir / 'manifest.csv'
    build_manifest(rtc_dir, manifest_path)
    print(f"Wrote manifest to {manifest_path}")


if __name__ == '__main__':
    main()
