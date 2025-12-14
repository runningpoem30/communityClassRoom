"""
AutoMaintainer AI - Create Pull Request
Creates a GitHub PR with the implemented changes.
"""

import os
import json
import argparse
from github import Github
import subprocess


def get_diff_stats(repo_path: str) -> dict:
    """Get statistics about changes"""
    try:
        # Get changed files
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        files_changed = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        # Get line changes
        result = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        lines_added = 0
        lines_deleted = 0
        for line in result.stdout.split('\n'):
            if '+' in line and '-' in line:
                parts = line.split(',')
                for part in parts:
                    if 'insertion' in part:
                        lines_added += int(part.split()[0])
                    if 'deletion' in part:
                        lines_deleted += int(part.split()[0])
        
        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted
        }
    except:
        return {'files_changed': 0, 'lines_added': 0, 'lines_deleted': 0}


def create_pr(repo_path: str, implementation: dict) -> dict:
    """Create GitHub pull request"""
    
    token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')
    bot_username = os.getenv('GITHUB_BOT_USERNAME', 'automaintainer-bot')
    
    # Create branch name
    task_title = implementation['task']['title']
    branch_name = f"automaintainer/{task_title.lower().replace(' ', '-')[:50]}"
    
    # Commit changes
    subprocess.run(['git', 'checkout', '-b', branch_name], cwd=repo_path)
    subprocess.run(['git', 'add', '.'], cwd=repo_path)
    subprocess.run(
        ['git', 'commit', '-m', f"[AutoMaintainer] {task_title}"],
        cwd=repo_path
    )
    
    # Push to remote
    subprocess.run(
        ['git', 'push', 'origin', branch_name, '--force'],
        cwd=repo_path,
        env={**os.environ, 'GIT_ASKPASS': 'echo', 'GIT_USERNAME': bot_username, 'GIT_PASSWORD': token}
    )
    
    # Create PR via GitHub API
    client = Github(token)
    repo = client.get_repo(f"{repo_owner}/{repo_name}")
    
    pr = repo.create_pull(
        title=task_title,
        body=implementation.get('pr_description', 'Automated improvement by AutoMaintainer AI'),
        head=branch_name,
        base='main'
    )
    
    stats = get_diff_stats(repo_path)
    
    return {
        'number': pr.number,
        'url': pr.html_url,
        'title': task_title,
        'description': pr.body,
        'status': 'open',
        **stats
    }


def main():
    parser = argparse.ArgumentParser(description='Create pull request')
    parser.add_argument('--repo', required=True, help='Repository path')
    parser.add_argument('--implementation', required=True, help='Implementation result JSON')
    args = parser.parse_args()
    
    # Load implementation data
    with open(args.implementation, 'r') as f:
        implementation = json.load(f)
    
    print("📤 Creating pull request...")
    
    pr_data = create_pr(args.repo, implementation)
    
    print(f"✓ Created PR #{pr_data['number']}: {pr_data['url']}")
    
    # Save output
    with open('pr_data.json', 'w') as f:
        json.dump(pr_data, f, indent=2)


if __name__ == '__main__':
    main()
