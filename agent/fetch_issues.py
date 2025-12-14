"""
AutoMaintainer AI - Fetch GitHub Issues
Retrieves open issues from target repository.
"""

import os
import json
from github import Github


def main():
    token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')
    
    if not all([token, repo_owner, repo_name]):
        print("⚠️  GitHub credentials not configured")
        # Return empty list
        with open('issues.json', 'w') as f:
            json.dump({'issues': []}, f)
        return
    
    print(f"📥 Fetching issues from {repo_owner}/{repo_name}...")
    
    client = Github(token)
    repo = client.get_repo(f"{repo_owner}/{repo_name}")
    
    # Get open issues
    issues = []
    for issue in repo.get_issues(state='open')[:20]:  # Limit to 20
        if not issue.pull_request:  # Exclude PRs
            issues.append({
                'number': issue.number,
                'title': issue.title,
                'body': (issue.body or '')[:500],  # Limit body length
                'labels': [label.name for label.labels],
                'created_at': issue.created_at.isoformat()
            })
    
    print(f"✓ Found {len(issues)} open issues")
    
    # Save output
    with open('issues.json', 'w') as f:
        json.dump({'issues': issues}, f, indent=2)


if __name__ == '__main__':
    main()
