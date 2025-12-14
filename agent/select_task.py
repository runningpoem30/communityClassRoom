"""
AutoMaintainer AI - Task Selection
Uses LLM to select one meaningful improvement task.
"""

import os
import json
import argparse

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def load_prompt_template(prompt_name: str) -> str:
    """Load prompt template from file"""
    prompt_path = f"/app/agent/prompts/{prompt_name}.md"
    with open(prompt_path, 'r') as f:
        return f.read()


def format_context(analysis: dict, issues: dict, learnings: dict) -> dict:
    """Format context data for the prompt"""
    
    # Format repository structure
    repo_structure = json.dumps(analysis.get('structure', {}), indent=2)
    
    # Format GitHub issues
    github_issues = "\n".join([
        f"- #{issue['number']}: {issue['title']}"
        for issue in issues.get('issues', [])[:10]
    ])
    if not github_issues:
        github_issues = "No open issues"
    
    # Format TODOs
    todo_list = "\n".join([
        f"- {todo['file']}:{todo['line']} - {todo['text']}"
        for todo in analysis.get('todos', [])[:20]
    ])
    if not todo_list:
        todo_list = "No TODOs found"
    
    # Format past PRs
    past_prs = "\n".join([
        f"- {pr['task_title']} ({pr['task_type']}) - Score: {pr.get('evolution_score', 'N/A')}/100, Status: {pr['merge_status']}"
        for pr in learnings.get('past_prs', [])[:5]
    ])
    if not past_prs:
        past_prs = "No past PRs (first run)"
    
    # Format negative feedback
    negative_feedback = "\n".join([
        f"- {mistake['summary']}"
        for mistake in learnings.get('mistakes', [])[:10]
    ])
    if not negative_feedback:
        negative_feedback = "None (maintain high standards!)"
    
    return {
        'repo_name': analysis.get('repo_name', 'unknown'),
        'repo_structure': repo_structure,
        'github_issues': github_issues,
        'todo_list': todo_list,
        'past_prs': past_prs,
        'negative_feedback': negative_feedback
    }


def select_task_with_llm(context: dict, model: str = "gemini-2.0-flash-exp") -> dict:
    """Use LLM to select a task - supports Gemini, Claude, or GPT-4"""
    
    # Load and format prompt
    prompt_template = load_prompt_template('task-selection')
    prompt = prompt_template.format(**context)
    
    # Determine provider from model name or environment
    if model.startswith('gemini') or os.getenv('GOOGLE_API_KEY'):
        # Use Gemini (FREE!)
        if not genai:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        gemini_model = genai.GenerativeModel(model or 'gemini-2.0-flash-exp')
        response = gemini_model.generate_content(prompt)
        response_text = response.text
        
    elif model.startswith('claude') or os.getenv('ANTHROPIC_API_KEY'):
        # Use Claude
        if not Anthropic:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
        
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text
        
    elif model.startswith('gpt') or os.getenv('OPENAI_API_KEY'):
        # Use OpenAI
        if not OpenAI:
            raise ImportError("openai not installed. Run: pip install openai")
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        response_text = response.choices[0].message.content
    else:
        raise ValueError(f"Unknown model: {model}. Use gemini-*, claude-*, or gpt-*")
    
    # Extract JSON from response
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("No JSON found in LLM response")
    
    task_data = json.loads(response_text[start:end])
    
    # Validate required fields
    required_fields = ['task_type', 'title', 'description', 'affected_files', 
                      'reasoning', 'risk_assessment', 'test_strategy']
    for field in required_fields:
        if field not in task_data:
            raise ValueError(f"Missing required field: {field}")
    
    return task_data


def main():
    parser = argparse.ArgumentParser(description='Select improvement task')
    parser.add_argument('--analysis', required=True, help='Path to analysis.json')
    parser.add_argument('--issues', required=True, help='Path to issues.json')
    parser.add_argument('--learnings', required=True, help='Path to learnings.json')
    args = parser.parse_args()
    
    # Load input data
    with open(args.analysis, 'r') as f:
        analysis = json.load(f)
    
    with open(args.issues, 'r') as f:
        issues = json.load(f)
    
    with open(args.learnings, 'r') as f:
        learnings = json.load(f)
    
    # Format context
    context = format_context(analysis, issues, learnings)
    
    # Select task
    print("🤖 Analyzing repository and selecting improvement task...")
    task = select_task_with_llm(context)
    
    print(f"✓ Selected task: {task['title']}")
    print(f"  Type: {task['task_type']}")
    print(f"  Risk: {task['risk_assessment']}")
    print(f"  Files: {len(task['affected_files'])}")
    
    # Save output
    with open('selected_task.json', 'w') as f:
        json.dump(task, f, indent=2)
    
    print("✓ Task selection complete. Output: selected_task.json")


if __name__ == '__main__':
    main()
