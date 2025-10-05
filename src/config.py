from datetime import date
from pathlib import Path

# Project configuration for Reykjanes Peninsula (NASA Space Apps)

# 1) AOI path
AOI_GEOJSON_PATH: str = 'aoi.geojson'

# 2) Date ranges
DATE_RANGES = {
    'pre': (date(2024, 5, 1), date(2024, 5, 31)),
    'during': (date(2024, 11, 1), date(2024, 11, 30)),
    'recent': (date(2025, 9, 1), date(2025, 10, 4)),
}

# 3) Output directories
OUTPUT_DIRS = {
    'raw': 'data/raw',
    'rtc': 'data/rtc',
    'outputs': 'outputs',
}

# 4) Map center [lat, lon]
MAP_CENTER = [63.95, -22.35]

# 5) HyP3 parameters
HYP3_PARAMS = {
    'radiometry': 'gamma0',
    'speckle_filter': True,
    'resolution': 30,
}

# Ensure directories exist when imported (safe on Windows)
for p in OUTPUT_DIRS.values():
    Path(p).mkdir(parents=True, exist_ok=True)
