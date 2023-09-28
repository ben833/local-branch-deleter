import os
import sys
import argparse
from datetime import datetime, timezone

from git import Repo

def delete_stale_branches(repo, days_threshold):
    remote_branches = [ref.split("refs/heads/")[1] for ref in repo.git.ls_remote("--heads", "--quiet").split() if ref.startswith("refs/heads/")]
    print(f"remote_branches: {remote_branches}")
    local_branches = [ref.path.split("refs/heads/")[1] for ref in repo.refs if ref.path.startswith("refs/heads/")]
    print(f"local_branches: {local_branches}")
    for branch in local_branches:
        if branch not in remote_branches:
            branch_ref = repo.heads[branch]
            last_commit_date = branch_ref.commit.committed_datetime
            today = datetime.now(timezone.utc)
            if (today - last_commit_date).days > days_threshold:
                print(f"Deleting local branch '{branch}'...")
                repo.git.branch("-d", branch)
            else:
                print(f"Not deleting '{branch}' because it's not old enough ...")

def main():
    parser = argparse.ArgumentParser(description="Delete local branches that are deleted on the production remote.")
    parser.add_argument("--repo-path", default=os.getcwd(), help="Path to the Git repository (default: current directory)")
    parser.add_argument("--days-threshold", type=int, default=120, help="Number of days to allow branches to exist locally after deletion on prod (default: 120)")
    args = parser.parse_args()

    try:
        repo = Repo(args.repo_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    delete_stale_branches(repo, args.days_threshold)

if __name__ == "__main__":
    main()
