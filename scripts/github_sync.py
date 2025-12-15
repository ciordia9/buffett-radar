#!/usr/bin/env python3
"""
GitHub Sync Utility for Buffett Radar
Handles cloning, pulling, and pushing to GitHub repository
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "ciordia9"
REPO_NAME = "buffett-radar"
REPO_URL = f"https://{GITHUB_TOKEN}@github.com/{REPO_OWNER}/{REPO_NAME}.git"
LOCAL_PATH = Path(__file__).parent.parent


def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def clone_repo():
    """Clone repository from GitHub"""
    parent_dir = LOCAL_PATH.parent
    
    print(f"Cloning {REPO_OWNER}/{REPO_NAME}...")
    result = run_command(f"git clone {REPO_URL}", cwd=parent_dir)
    
    if result is not None:
        print("✓ Repository cloned successfully")
        return True
    return False


def pull_latest():
    """Pull latest changes from GitHub"""
    print("Pulling latest changes from GitHub...")
    
    # Check if we're in a git repository
    if not (LOCAL_PATH / ".git").exists():
        print("Not a git repository. Initializing...")
        run_command("git init", cwd=LOCAL_PATH)
        run_command(f"git remote add origin {REPO_URL}", cwd=LOCAL_PATH)
    
    # Fetch and pull
    run_command("git fetch origin", cwd=LOCAL_PATH)
    result = run_command("git pull origin main", cwd=LOCAL_PATH)
    
    if result is not None:
        print("✓ Pulled latest changes")
        return True
    else:
        # Try master branch if main doesn't exist
        result = run_command("git pull origin master", cwd=LOCAL_PATH)
        if result is not None:
            print("✓ Pulled latest changes from master")
            return True
    
    return False


def commit_and_push(message):
    """Commit changes and push to GitHub"""
    print(f"\nCommitting changes: {message}")
    
    # Configure git user if not set
    run_command('git config user.email "manus@ai.com"', cwd=LOCAL_PATH)
    run_command('git config user.name "Manus AI"', cwd=LOCAL_PATH)
    
    # Add all changes
    run_command("git add .", cwd=LOCAL_PATH)
    
    # Check if there are changes to commit
    status = run_command("git status --porcelain", cwd=LOCAL_PATH)
    if not status:
        print("No changes to commit")
        return True
    
    # Commit
    result = run_command(f'git commit -m "{message}"', cwd=LOCAL_PATH)
    if result is None:
        print("Failed to commit changes")
        return False
    
    print("✓ Changes committed")
    
    # Push to remote
    print("Pushing to GitHub...")
    
    # Determine current branch
    branch = run_command("git branch --show-current", cwd=LOCAL_PATH)
    if not branch:
        branch = "main"
    
    result = run_command(f"git push origin {branch}", cwd=LOCAL_PATH)
    
    if result is not None:
        print(f"✓ Pushed to GitHub ({branch} branch)")
        return True
    else:
        print("Failed to push to GitHub")
        return False


def get_status():
    """Get current git status"""
    status = run_command("git status --short", cwd=LOCAL_PATH)
    return status if status else "No changes"


def main():
    """Main function for command-line usage"""
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python github_sync.py [pull|push|status]")
        print("  pull   - Pull latest changes from GitHub")
        print("  push   - Commit and push changes to GitHub")
        print("  status - Show current git status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "pull":
        pull_latest()
    elif command == "push":
        message = sys.argv[2] if len(sys.argv) > 2 else "Update from Manus AI"
        commit_and_push(message)
    elif command == "status":
        status = get_status()
        print(f"Status:\n{status}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
