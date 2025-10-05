"""
Submit HyP3 RTC jobs for Sentinel-1 GRD (IW, ASCENDING) over Reykjanes.

Usage:
  python src/submit_hyp3_jobs.py --limit 2  # per period
  python src/submit_hyp3_jobs.py --dry-run

Requires Earthdata authentication for ASF (asf-search) and HyP3 account/token.
See QUICKSTART.md for .netrc and login steps.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List
import sys
import time
import click
import asf_search as asf
from shapely.geometry import shape
from hyp3_sdk import HyP3

from config import AOI_GEOJSON_PATH, DATE_RANGES, OUTPUT_DIRS, HYP3_PARAMS


def load_wkt(geojson_path: Path) -> str:
    """Load WKT geometry from GeoJSON file."""
    gj = json.loads(Path(geojson_path).read_text())
    geom = gj['features'][0]['geometry'] if gj.get('type') == 'FeatureCollection' else (
        gj['geometry'] if gj.get('type') == 'Feature' else gj
    )
    return shape(geom).wkt


def normalize_granule_name(granule_raw: str) -> str:
    """
    Normalize granule name by removing product suffixes.
    
    HyP3 expects base granule names without suffixes like:
    - -SLC, -GRD_HD, -GRD_MD, -GRD_FD
    """
    granule = granule_raw.strip()
    
    # Remove common suffixes
    suffixes = ['-SLC', '-GRD_HD', '-GRD_MD', '-GRD_FD', '-RAW']
    for suffix in suffixes:
        if granule.endswith(suffix):
            granule = granule[:-len(suffix)]
            break
    
    return granule


def is_supported_satellite(scene_name: str) -> bool:
    """
    Check if satellite is supported by HyP3 RTC processing.
    
    Currently only S1A (Sentinel-1A) and S1B (Sentinel-1B) are supported.
    S1C (Sentinel-1C, launched 2024) is not yet supported.
    """
    return scene_name.startswith(('S1A_', 'S1B_'))


@click.command()
@click.option('--limit', default=2, show_default=True, help='Scenes per period (to limit volume).')
@click.option('--dry-run', is_flag=True, help='Search only; do not submit jobs.')
def main(limit: int, dry_run: bool) -> None:
    """Submit HyP3 RTC jobs for Sentinel-1 scenes over Reykjanes Peninsula."""
    data_dir = Path(OUTPUT_DIRS['raw']).parent
    jobs_meta_path = data_dir / 'hyp3_jobs.json'
    aoi_wkt = load_wkt(Path(AOI_GEOJSON_PATH))

    # Search per period
    all_results: Dict[str, List[asf.ASFSearchResult]] = {}
    for period, (start_d, end_d) in DATE_RANGES.items():
        print(f"Searching ASF for period '{period}' {start_d}..{end_d} (IW, ASCENDING)")
        try:
            # Search for GRD products (pre-processed, ready for RTC)
            results = asf.search(
                platform=asf.PLATFORM.SENTINEL1,
                processingLevel=asf.PRODUCT_TYPE.GRD_HD,  # High-res GRD
                beamMode=asf.BEAMMODE.IW,
                flightDirection='ASCENDING',
                intersectsWith=aoi_wkt,
                start=str(start_d), 
                end=str(end_d),
            )
        except Exception as e:
            print(f"ASF search failed for {period}: {e}", file=sys.stderr)
            results = []
        
        # Filter to supported satellites (S1A/S1B only; exclude S1C)
        initial_count = len(results)
        results = [r for r in results if is_supported_satellite(
            r.properties.get('sceneName') or r.properties.get('fileID') or ''
        )]
        
        if initial_count > len(results):
            print(f"  Filtered out {initial_count - len(results)} unsupported scenes (S1C)")
        
        # Sort by acquisition date (newest first), then limit
        results = sorted(
            results, 
            key=lambda r: r.properties.get('startTime', ''), 
            reverse=True
        )[:limit]
        
        print(f"  Found {len(results)} supported scenes (limited to {limit})")
        all_results[period] = results

    if dry_run:
        print('\nDry run complete. No jobs submitted.')
        for period, results in all_results.items():
            print(f"\n{period.upper()}:")
            for r in results:
                scene = r.properties.get('sceneName', 'unknown')
                print(f"  - {scene}")
        return

    # Submit RTC jobs
    hyp3 = HyP3()
    submitted = []
    failed = []

    for period, results in all_results.items():
        for r in results:
            scene_name = r.properties.get('sceneName', 's1')
            name = f"reykjanes_{period}_{scene_name}"[:80]  # HyP3 name limit
            
            try:
                # Get granule identifier
                granule_raw = (
                    r.properties.get('fileID') or 
                    r.properties.get('granuleName') or 
                    r.properties.get('sceneName')
                )
                
                if not granule_raw:
                    raise ValueError('Missing granule identifier in ASF result')
                
                # Normalize granule name
                granule = normalize_granule_name(granule_raw)
                
                if not granule:
                    raise ValueError(f'Invalid granule parsed from {granule_raw!r}')
                
                print(f"\nSubmitting: {granule}")
                print(f"  Period: {period}")
                print(f"  Job name: {name}")
                
                # Submit RTC job with parameters from config
                batch = hyp3.submit_rtc_job(
                    granule=granule,
                    name=name,
                    include_dem=HYP3_PARAMS.get('include_dem', False),
                    include_inc_map=HYP3_PARAMS.get('include_inc_map', False),
                    include_rgb=HYP3_PARAMS.get('include_rgb', False),
                    include_scattering_area=HYP3_PARAMS.get('include_scattering_area', False),
                    radiometry=HYP3_PARAMS.get('radiometry', 'gamma0'),
                    resolution=HYP3_PARAMS.get('resolution', 30),
                    scale=HYP3_PARAMS.get('scale', 'power'),
                    speckle_filter=HYP3_PARAMS.get('speckle_filter', False),
                    dem_name=HYP3_PARAMS.get('dem_name', 'copernicus'),
                )
                
                # Handle Batch response (hyp3-sdk 7.7.3+)
                if hasattr(batch, 'jobs') and batch.jobs:
                    job = batch.jobs[0]
                    job_info = {
                        'period': period,
                        'name': job.name,
                        'job_id': job.job_id,
                        'granule': granule,
                        'status': job.status_code,
                    }
                    submitted.append(job_info)
                    print(f"  ✓ Job ID: {job.job_id}")
                    print(f"  Status: {job.status_code}")
                else:
                    raise ValueError("Unexpected response format from HyP3")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"  ✗ Submit failed: {error_msg}", file=sys.stderr)
                failed.append({
                    'period': period,
                    'granule': granule_raw if 'granule_raw' in locals() else scene_name,
                    'error': error_msg
                })

    # Save metadata
    jobs_meta = {
        'submitted': submitted,
        'failed': failed,
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'params': {
            'radiometry': HYP3_PARAMS.get('radiometry', 'gamma0'),
            'speckle_filter': HYP3_PARAMS.get('speckle_filter', False),
            'resolution': HYP3_PARAMS.get('resolution', 30),
            'limit_per_period': limit,
        }
    }
    
    jobs_meta_path.write_text(json.dumps(jobs_meta, indent=2))
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Jobs submitted: {len(submitted)}")
    print(f"Jobs failed: {len(failed)}")
    print(f"Metadata saved to: {jobs_meta_path}")
    
    if submitted:
        print("\nJobs typically complete in 10-30 minutes.")
        print("Check status with: hyp3 watch")
        print("Or run: python src/download_hyp3_results.py")
    
    if failed:
        print("\nFailed submissions:")
        for f in failed:
            print(f"  {f['period']}: {f['granule']}")
            print(f"    Error: {f['error']}")


if __name__ == '__main__':
    main()