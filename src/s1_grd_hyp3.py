import json
import os
from datetime import datetime
import click
import asf_search as asf
from hyp3_sdk import HyP3, util
from shapely.geometry import shape, box, mapping


def load_wkt_from_geojson(path: str) -> str:
    with open(path, 'r') as f:
        gj = json.load(f)
    if gj.get('type') == 'FeatureCollection':
        geom = gj['features'][0]['geometry']
    elif gj.get('type') == 'Feature':
        geom = gj['geometry']
    else:
        geom = gj
    return shape(geom).wkt


def bbox_to_wkt(w, s, e, n) -> str:
    return box(w, s, e, n).wkt


@click.command()
@click.option('--aoi', type=click.Path(exists=True), help='Path to AOI GeoJSON (Feature/FeatureCollection/Geometry).')
@click.option('--bbox', nargs=4, type=float, help='AOI bbox: W S E N (floats).')
@click.option('--start', required=True, help='Start date YYYY-MM-DD')
@click.option('--end', required=True, help='End date YYYY-MM-DD')
@click.option('--beam', default='IW', show_default=True)
@click.option('--radiometry', default='Gamma0', type=click.Choice(['Gamma0','Sigma0']), show_default=True)
@click.option('--outdir', default='data/rtc', show_default=True)
@click.option('--flight', type=click.Choice(['ASCENDING','DESCENDING']), default=None)
def main(aoi, bbox, start, end, beam, radiometry, outdir, flight):
    os.makedirs(outdir, exist_ok=True)
    # AOI WKT
    if aoi:
        wkt = load_wkt_from_geojson(aoi)
    elif bbox:
        wkt = bbox_to_wkt(*bbox)
    else:
        raise click.UsageError('Provide either --aoi or --bbox')

    # Search Sentinel-1 GRD
    search_kwargs = dict(
        platform=asf.PLATFORM.SENTINEL1,
        processingLevel=asf.PRODUCT_TYPE.GRD_HD,
        beamMode=getattr(asf.BEAMMODE, beam),
        intersectsWith=wkt,
        start=start, end=end,
    )
    if flight:
        search_kwargs['flightDirection'] = flight

    print('Searching ASF...')
    results = asf.search(**search_kwargs)
    print(f'Found {len(results)} scenes')
    if not results:
        return

    hyp3 = HyP3()
    jobs = []
    for r in results:
        jobs.append(hyp3.submit_rtc_job(r, apply_thermal_noise_removal=True, radiometry=radiometry))
    print(f'Submitted {len(jobs)} RTC jobs to HyP3')

    batch = util.Batch(jobs)
    batch = batch.watch()
    print('Jobs complete. Downloading...')
    batch.download(outdir)
    print(f'Downloaded to {outdir}')


if __name__ == '__main__':
    main()
