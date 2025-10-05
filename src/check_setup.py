"""
Environment diagnostics for the NASA Space Apps SAR project (Windows-friendly).

Usage:
  python src/check_setup.py
"""
from __future__ import annotations
import json
import os
import platform
import shutil
from pathlib import Path
from typing import List

REQUIRED_PACKAGES: List[str] = [
    'asf_search', 'hyp3_sdk', 'rasterio', 'numpy', 'pandas', 'matplotlib', 'folium'
]

HOME = Path.home()


def _ok(msg: str) -> None:
    print(f"[OK] {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def check_python() -> None:
    ver = platform.python_version()
    major, minor, _ = map(int, ver.split('.'))
    if major > 3 or (major == 3 and minor >= 9):
        _ok(f"Python version {ver}")
    else:
        _fail(f"Python {ver} detected; please use >= 3.9")


def check_packages() -> None:
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except Exception:
            missing.append(pkg)
    if missing:
        _fail(f"Missing packages: {', '.join(missing)}. Run: pip install -r requirements.txt")
    else:
        _ok("All required packages import successfully")


def check_netrc() -> None:
    netrc = HOME / '.netrc'
    if netrc.exists():
        txt = netrc.read_text(errors='ignore')
        if 'urs.earthdata.nasa.gov' in txt:
            _ok(".netrc found with Earthdata host")
        else:
            _warn(".netrc found but missing urs.earthdata.nasa.gov entry")
    else:
        _warn(".netrc not found. HyP3/ASF may prompt for login on first use")


def check_disk_space() -> None:
    total, used, free = shutil.disk_usage(str(Path.cwd()))
    gb_free = free / (1024**3)
    if gb_free < 50:
        _warn(f"Low disk space: {gb_free:.1f} GB free (recommend >= 50 GB)")
    else:
        _ok(f"Disk space OK: {gb_free:.1f} GB free")


def check_hyp3() -> None:
    try:
        from hyp3_sdk import HyP3
        hyp3 = HyP3()
        # Attempt a lightweight call (may be a no-op if not authenticated)
        _ok("HyP3 SDK initialized")
    except Exception as e:
        _warn(f"HyP3 init failed: {e}")


def check_aoi() -> None:
    aoi = Path('aoi.geojson')
    if not aoi.exists():
        _fail('aoi.geojson is missing')
        return
    try:
        gj = json.loads(aoi.read_text())
        assert gj.get('type') in ('FeatureCollection','Feature','Polygon')
        _ok('aoi.geojson is valid JSON/GeoJSON')
    except Exception as e:
        _fail(f'aoi.geojson invalid: {e}')


def main() -> None:
    print('--- Environment Check ---')
    check_python()
    check_packages()
    check_netrc()
    check_disk_space()
    check_hyp3()
    check_aoi()
    print('--- Done ---')


if __name__ == '__main__':
    main()
