#!/usr/bin/env python3
"""
Automated Weekly Buffett Radar Update
Complete closed-loop workflow: pull, update, analyze, commit, push
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules - use subprocess to run scripts
import subprocess
import json
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")


def main():
    """Run complete weekly update workflow"""
    
    print_header("BUFFETT RADAR: AUTOMATED WEEKLY UPDATE")
    
    #    # Step 1: Sync from GitHub
    print_header("STEP 1: Sync from GitHub")
    
    script_dir = Path(__file__).parent
    result = subprocess.run(
        ["python3", str(script_dir / "github_sync.py"), "pull"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print("Warning: Could not pull from GitHub. Continuing with local data...")
    
    # Step 2: Fetch new data
    print_header("STEP 2: Fetch Latest Data")
    
    script_dir = Path(__file__).parent
    result = subprocess.run(
        ["python3", str(script_dir / "update_weekly_data.py")],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running update_weekly_data.py: {result.stderr}")
        return
    
    print(result.stdout)
    
    # Find the most recent weekly file
    data_dir = script_dir.parent / "data" / "weekly"
    week_files = sorted(data_dir.glob("*.json"), reverse=True)
    if not week_files:
        print("Error: No weekly data files found")
        return
    
    with open(week_files[0]) as f:
        snapshot = json.load(f)
    
    week_id = snapshot['week_id']
    
    # Step 3: Analyze trends
    print_header("STEP 3: Analyze Trends")
    
    result = subprocess.run(
        ["python3", str(script_dir / "analyze_trends.py")],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Check if changes file was created
    changes_file = script_dir.parent / "reports" / week_id / "changes.json"
    changes_data = None
    if changes_file.exists():
        with open(changes_file) as f:
            changes_data = json.load(f)
    
    # Step 4: Commit and push to GitHub
    print_header("STEP 4: Push to GitHub")
    
    commit_message = f"Weekly update: {week_id} - Automated by Manus AI"
    
    result = subprocess.run(
        ["python3", str(script_dir / "github_sync.py"), "push", commit_message],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode == 0:
        print("\n✓ Successfully pushed to GitHub")
    else:
        print("\n⚠ Could not push to GitHub")
        print("  Changes are saved locally. You can manually push later.")
        if result.stderr:
            print(f"  Error: {result.stderr}")
    
    # Summary
    print_header("WEEKLY UPDATE COMPLETE")
    print(f"Week: {snapshot['week_id']}")
    print(f"Date Range: {snapshot['date_range']['start']} to {snapshot['date_range']['end']}")
    print(f"Data File: {week_files[0]}")
    
    if changes_data:
        print(f"\nChanges Detected:")
        print(f"  Total: {changes_data['summary']['total_changes']}")
        print(f"  Critical: {changes_data['summary']['critical_changes']}")
        print(f"  High: {changes_data['summary']['high_significance']}")
    
    print("\n✓ All done! Check GitHub for the latest commit.")
    print(f"  https://github.com/ciordia9/buffett-radar/tree/main")


if __name__ == "__main__":
    main()
