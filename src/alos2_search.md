# ALOS-2 L-band Data (Acquisition Plan)

## Source
- ASF Vertex (https://search.asf.alaska.edu/). Some ALOS-2 datasets require access approval. Use your Earthdata login.

## Programmatic search (concept)
Using `asf-search`:

```python
import asf_search as asf
from shapely.geometry import box

wkt = box(-22.70, 63.80, -22.00, 64.10).wkt
results = asf.search(
    platform=asf.PLATFORM.ALOS2,
    intersectsWith=wkt,
    start='2024-06-01', end='2025-10-01',
    beamMode=None,  # e.g., 'SM', 'WB1' depending on product; check ASF docs
)
print(len(results))
for r in results[:10]:
    print(r.properties.get('processingLevel'), r.properties.get('fileID'))
```

## Notes
- Prefer SLC (for coherence) if available; else RTC backscatter for multi-frequency comparison.
- Match geometry and incidence angle where possible.
- After download, co-register L-band to C-band grid (resample) before pixel-wise comparisons.
