"""
Master batch script to run the end-to-end GRD pipeline with HyP3.

Usage:
  python src/batch_process.py --skip-download
Steps:
  1) submit_hyp3_jobs (unless --skip-download)
  2) download_hyp3_results
  3) analyze_backscatter (ratios + delta)
  4) statistics summary
  5) create_web_map (single and dual)
Generates a log at outputs/pipeline.log and a summary at outputs/summary.txt
"""
from __future__ import annotations
import subprocess
from pathlib import Path
import sys
import time

LOG_PATH = Path('outputs/pipeline.log')
SUMMARY_PATH = Path('outputs/summary.txt')


def run(cmd: list[str], allow_fail: bool = True) -> int:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open('a', encoding='utf-8') as log:
        log.write(f"\n$ {' '.join(cmd)}\n")
        log.flush()
        proc = subprocess.run(cmd, stdout=log, stderr=log, text=True)
        rc = proc.returncode
        if rc != 0 and not allow_fail:
            print('Command failed, see log:', ' '.join(cmd))
            sys.exit(rc)
        return rc


def main(skip_download: bool = False) -> None:
    LOG_PATH.write_text(f"Pipeline started {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    if not skip_download:
        run([sys.executable, 'src/submit_hyp3_jobs.py', '--limit', '2'])
        print('Submitted jobs. Wait for completion before continuing download step.')

    run([sys.executable, 'src/download_hyp3_results.py'])

    # Analyze ratios
    manifest = Path('data/rtc/manifest.csv')
    if manifest.exists():
        run([sys.executable, 'src/analyze_backscatter.py', '--manifest', str(manifest), '--output-dir', 'outputs', '--make-plots'])
        # Stats (best-effort: try recent vs pre if created)
        # create_web_map single and dual
        # Find ratio files
        ratio_pre = next(Path('outputs').glob('ratio_pre_*.tif'), None)
        ratio_recent = next(Path('outputs').glob('ratio_recent_*.tif'), None)
        if ratio_pre and ratio_recent:
            run([sys.executable, 'src/statistics.py', '--compare', str(ratio_pre), str(ratio_recent), '--out', 'outputs/stats.csv'])
            run([sys.executable, 'src/create_web_map.py', '--mode', 'dual', '--layers', str(ratio_pre), str(ratio_recent), '--out', 'outputs/dual.html'])
        # Single map: add delta if available
        delta = next(Path('outputs').glob('ratio_delta_*.tif'), None)
        if delta:
            run([sys.executable, 'src/create_web_map.py', '--mode', 'single', '--layers', str(delta), '--out', 'outputs/map.html'])

    # Export figures
    run([sys.executable, 'src/export_figures.py'])

    SUMMARY_PATH.write_text('Pipeline completed. See outputs/ for results and outputs/pipeline.log for logs.\n')
    print('Done. Summary at', SUMMARY_PATH)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-download', action='store_true', help='Skip submitting jobs (use existing data)')
    args = ap.parse_args()
    main(skip_download=args.skip_download)
