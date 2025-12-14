"""
AutoMaintainer AI - Store Results
Persists all run data to PostgreSQL.
"""

import os
import sys
import json
import argparse
sys.path.append('/app/memory')
from memory_manager import MemoryManager


def main():
    parser = argparse.ArgumentParser(description='Store run results')
    parser.add_argument('--task', required=True, help='Path to task JSON')
    parser.add_argument('--pr', required=True, help='Path to PR JSON')
    parser.add_argument('--review', required=True, help='Path to review JSON')
    parser.add_argument('--evaluation', required=True, help='Path to evaluation JSON')
    args = parser.parse_args()
    
    # Load all data
    with open(args.task, 'r') as f:
        task = json.load(f)
    
    with open(args.pr, 'r') as f:
        pr_data = json.load(f)
    
    with open(args.review, 'r') as f:
        review = json.load(f)
    
    with open(args.evaluation, 'r') as f:
        evaluation = json.load(f)
    
    # Store in database
    mm = MemoryManager()
    
    print("📝 Storing results in database...")
    
    # 1. Create agent run
    run_id = mm.create_agent_run(task)
    print(f"✓ Created agent run #{run_id}")
    
    # 2. Create PR record
    pr_id = mm.create_pull_request(run_id, pr_data)
    print(f"✓ Created PR record #{pr_id}")
    
    # 3. Store code review
    review_id = mm.create_code_review(pr_id, review)
    print(f"✓ Stored code review #{review_id}")
    
    # 4. Store evaluation
    eval_id = mm.create_evaluation(pr_id, evaluation)
    print(f"✓ Stored evaluation #{eval_id}")
    
    # 5. Update run status
    mm.update_run_status(
        run_id,
        status='success',
        summary=f"Completed {task['task_type']}: {task['title']}",
        pr_url=pr_data['url']
    )
    print(f"✓ Updated run status to success")
    
    # Save run ID for next step
    with open('stored_run_id.txt', 'w') as f:
        f.write(str(run_id))
    
    print(f"✅ All results stored successfully. Run ID: {run_id}")


if __name__ == '__main__':
    main()
