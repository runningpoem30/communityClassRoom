"""
AutoMaintainer AI - Retrieve Past Learnings
Fetches relevant learnings from memory to provide as context.
"""

import os
import sys
import json
sys.path.append('/app/memory')
from memory_manager import MemoryManager


def main():
    mm = MemoryManager()
    
    # Get positive learnings (success patterns)
    learnings = mm.get_learnings(limit=15, min_importance=0.4)
    
    # Get negative feedback (mistakes to avoid)
    mistakes = mm.get_negative_feedback(limit=10)
    
    # Get past PR history
    past_prs = mm.get_past_prs(limit=5)
    
    # Compile into context
    context = {
        'learnings': [
            {
                'type': l['learning_type'],
                'summary': l['summary'],
                'context': l.get('context', {}),
                'importance': float(l.get('importance_score', 0.5))
            }
            for l in learnings
        ],
        'mistakes': [
            {
                'summary': m['summary'],
                'score': int(m.get('evolution_score', 0)),
                'pr_title': m.get('pr_title', 'Unknown')
            }
            for m in mistakes
        ],
        'past_prs': [
            {
                'task_title': p.get('task_title', 'Unknown'),
                'task_type': p.get('task_type', 'unknown'),
                'merge_status': p.get('merge_status', 'open'),
                'evolution_score': int(p['evolution_score']) if p.get('evolution_score') else None
            }
            for p in past_prs
        ]
    }
    
    # Generate summary for agent context
    positive_summary = "\n".join([
        f"- {l['summary']}"
        for l in learnings[:5]
    ]) if learnings else "No past learnings yet (first run)"
    
    negative_summary = "\n".join([
        f"- {m['summary']} (Score: {m['score']}/100)"
        for m in mistakes[:5]
    ]) if mistakes else "No mistakes recorded (maintain high standards!)"
    
    context['feedback_summary'] = f"""
## Success Patterns (Repeat These)
{positive_summary}

## Mistakes to Avoid
{negative_summary}
"""
    
    # Save output
    with open('learnings.json', 'w') as f:
        json.dump(context, f, indent=2)
    
    print(f"✓ Retrieved {len(learnings)} learnings, {len(mistakes)} mistakes, {len(past_prs)} past PRs")


if __name__ == '__main__':
    main()
