"""
Check status of submitted HyP3 jobs.

Usage:
  python src/check_status.py
"""
from pathlib import Path
import json
from hyp3_sdk import HyP3
from datetime import datetime

def main():
    # Load job metadata
    jobs_meta_path = Path('data/hyp3_jobs.json')
    
    if not jobs_meta_path.exists():
        print("❌ No jobs metadata found. Run submit_hyp3_jobs.py first.")
        return
    
    jobs_meta = json.loads(jobs_meta_path.read_text())
    submitted = jobs_meta.get('submitted', [])
    
    if not submitted:
        print("❌ No jobs were successfully submitted.")
        return
    
    print(f"Checking status of {len(submitted)} jobs...\n")
    print("=" * 80)
    
    # Connect to HyP3
    hyp3 = HyP3()
    
    # Get job IDs
    job_ids = [job['job_id'] for job in submitted if job.get('job_id')]
    
    if not job_ids:
        print("❌ No valid job IDs found in metadata.")
        return
    
    # Fetch current status - get all recent jobs and filter by our job IDs
    try:
        # Get recent jobs (last 7 days) and filter by our job IDs
        batch = hyp3.find_jobs()
        jobs_by_id = {job.job_id: job for job in batch if job.job_id in job_ids}
    except Exception as e:
        print(f"❌ Error fetching jobs: {e}")
        return
    
    # Status counters
    status_count = {'SUCCEEDED': 0, 'RUNNING': 0, 'PENDING': 0, 'FAILED': 0}
    
    # Display each job
    for job_meta in submitted:
        job_id = job_meta.get('job_id')
        period = job_meta.get('period', 'unknown')
        name = job_meta.get('name', 'unknown')
        
        if job_id in jobs_by_id:
            job = jobs_by_id[job_id]
            status = job.status_code
            status_count[status] = status_count.get(status, 0) + 1
            
            # Status emoji (Windows-safe)
            emoji = {
                'SUCCEEDED': '[OK]',
                'RUNNING': '[RUN]',
                'PENDING': '[PEND]',
                'FAILED': '[FAIL]'
            }.get(status, '[?]')
            
            print(f"{emoji} [{period.upper()}] {name[:50]}")
            print(f"   Status: {status}")
            print(f"   Job ID: {job_id}")
            
            if status == 'SUCCEEDED':
                if hasattr(job, 'files') and job.files:
                    print(f"   Files: {len(job.files)} ready for download")
            elif status == 'FAILED':
                print(f"   [WARN] Check HyP3 web interface for error details")
            
            print()
        else:
            print(f"[?] [{period.upper()}] {name[:50]}")
            print(f"   Job ID not found in HyP3 (may have been deleted)")
            print()
    
    print("=" * 80)
    print("\nSUMMARY:")
    print(f"  [OK] Succeeded: {status_count['SUCCEEDED']}")
    print(f"  [RUN] Running:   {status_count['RUNNING']}")
    print(f"  [PEND] Pending:   {status_count['PENDING']}")
    print(f"  [FAIL] Failed:    {status_count['FAILED']}")
    
    # Next steps
    if status_count['SUCCEEDED'] > 0:
        print("\n[SUCCESS] Some jobs are complete!")
        print("   Next step: python src/download_hyp3_results.py")
    elif status_count['RUNNING'] > 0 or status_count['PENDING'] > 0:
        print("\n[WAIT] Jobs still processing...")
        print("   Check again in 10-15 minutes")
        print("   Or run: hyp3 watch")
    elif status_count['FAILED'] > 0:
        print("\n[WARN] Some jobs failed. Check HyP3 web interface:")
        print("   https://hyp3-sdk.readthedocs.io/")

if __name__ == '__main__':
    main()