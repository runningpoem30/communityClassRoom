"""
AutoMaintainer AI - Oumi Evaluator
Custom evaluation functions for PR quality assessment.
"""

import os
import json
import argparse
from typing import Dict
import subprocess

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def evaluate_code_quality(pr_data: Dict) -> float:
    """
    Evaluate code quality using complexity analysis.
    Returns score 0-100.
    """
    # Use radon for complexity analysis
    # This is a simplified version - in production, analyze actual diff
    
    complexity_score = 75.0  # Base score
    
    # Factors that affect score:
    # - Low cyclomatic complexity: +points
    # - Good naming: +points
    # - Proper error handling: +points
    # - Code duplication: -points
    
    files_changed = pr_data.get('files_changed', 0)
    lines_added = pr_data.get('lines_added', 0)
    
    # Penalize huge changes
    if lines_added > 500:
        complexity_score -= 15
    elif lines_added > 200:
        complexity_score -= 5
    
    # Reward focused changes
    if files_changed <= 3 and lines_added < 100:
        complexity_score += 10
    
    return max(0, min(100, complexity_score))


def evaluate_test_coverage(pr_data: Dict) -> float:
    """
    Evaluate test coverage based on test file changes.
    Returns score 0-100.
    """
    test_score = 50.0  # Base score
    
    # Check if test files were modified
    # In production, run actual coverage tools
    
    # Heuristic: check PR description for test mentions
    description = pr_data.get('description', '').lower()
    
    if 'test' in description:
        test_score += 20
    if 'coverage' in description:
        test_score += 10
    if 'unit test' in description or 'integration test' in description:
        test_score += 15
    
    # Check files changed
    # In production, actually parse diff
    if pr_data.get('files_changed', 0) > 0:
        test_score += 5
    
    return max(0, min(100, test_score))


def evaluate_maintainability(review_data: Dict, pr_data: Dict) -> float:
    """
    Evaluate long-term maintainability.
    Returns score 0-100.
    """
    maintainability = 70.0  # Base score
    
    # Factors from CodeRabbit review
    security_issues = review_data.get('security_issues', 0)
    performance_issues = review_data.get('performance_issues', 0)
    style_issues = review_data.get('style_issues', 0)
    
    # Deduct for issues
    maintainability -= security_issues * 10
    maintainability -= performance_issues * 5
    maintainability -= style_issues * 2
    
    # Reward good practices
    if security_issues == 0:
        maintainability += 10
    
    # Check description quality
    description = pr_data.get('description', '')
    if len(description) > 100:  # Good description
        maintainability += 10
    
    return max(0, min(100, maintainability))


def evaluate_readability(pr_data: Dict, review_data: Dict) -> float:
    """
    Evaluate code readability.
    Returns score 0-100.
    """
    readability = 70.0  # Base score
    
    # Factors:
    # - Clear variable names
    # - Good comments
    # - Logical structure
    
    # Use CodeRabbit complexity as proxy
    complexity = review_data.get('complexity_score', 5.0)
    
    if complexity < 5:
        readability += 15
    elif complexity > 10:
        readability -= 15
    
    # Check for documentation
    description = pr_data.get('description', '')
    if 'documentation' in description.lower() or 'README' in description:
        readability += 10
    
    return max(0, min(100, readability))


def calculate_evolution_score(metrics: Dict) -> int:
    """
    Calculate composite Evolution Score.
    Weighted average of all metrics.
    """
    weights = {
        'code_quality': 0.30,
        'test_coverage': 0.25,
        'maintainability': 0.25,
        'readability': 0.20
    }
    
    score = (
        metrics['code_quality_score'] * weights['code_quality'] +
        metrics['test_coverage_score'] * weights['test_coverage'] +
        metrics['maintainability_score'] * weights['maintainability'] +
        metrics['readability_score'] * weights['readability']
    )
    
    return int(round(score))


def get_llm_evaluation(pr_data: Dict, review_data: Dict) -> Dict:
    """
    Use LLM to provide qualitative evaluation.
    This is the "Oumi" integration - using LLM for evaluation.
    Supports Gemini (free) or OpenAI.
    """
    model = os.getenv('OUMI_MODEL', 'gemini-2.0-flash-exp')
    
    prompt = f"""
You are an expert code reviewer evaluating a pull request.

PR Title: {pr_data.get('title')}
Description: {pr_data.get('description')}
Files Changed: {pr_data.get('files_changed')}
Lines Added: {pr_data.get('lines_added')}

CodeRabbit Review Summary:
{review_data.get('summary', 'No review available')}

Evaluate this PR on a scale of 0-100 for:
1. Overall quality
2. Likelihood of introducing bugs
3. Alignment with best practices

Provide a brief assessment (2-3 sentences) explaining the score.

Respond in JSON format:
{{
  "llm_score": <0-100>,
  "assessment": "Brief explanation"
}}
"""
    
    # Use Gemini or OpenAI based on model
    if model.startswith('gemini'):
        if not genai:
            return {"llm_score": 70, "assessment": "google-generativeai not installed"}
        
        genai.configure(api_key=os.getenv('OUMI_API_KEY') or os.getenv('GOOGLE_API_KEY'))
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(prompt)
        response_text = response.text
    else:
        if not OpenAI:
            return {"llm_score": 70, "assessment": "openai not installed"}
        
        client = OpenAI(api_key=os.getenv('OUMI_API_KEY'))
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        response_text = response.choices[0].message.content

    
    # Parse JSON
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    
    if start != -1 and end > 0:
        return json.loads(response_text[start:end])
    else:
        return {"llm_score": 70, "assessment": "Could not parse LLM response"}


def main():
    parser = argparse.ArgumentParser(description='Evaluate PR quality')
    parser.add_argument('--pr-data', required=True, help='Path to PR JSON')
    parser.add_argument('--review', required=True, help='Path to review JSON')
    args = parser.parse_args()
    
    # Load input
    with open(args.pr_data, 'r') as f:
        pr_data = json.load(f)
    
    with open(args.review, 'r') as f:
        review_data = json.load(f)
    
    print("🔍 Evaluating PR quality...")
    
    # Run all evaluations
    code_quality = evaluate_code_quality(pr_data)
    test_coverage = evaluate_test_coverage(pr_data)
    maintainability = evaluate_maintainability(review_data, pr_data)
    readability = evaluate_readability(pr_data, review_data)
    
    print(f"  Code Quality: {code_quality:.1f}/100")
    print(f"  Test Coverage: {test_coverage:.1f}/100")
    print(f"  Maintainability: {maintainability:.1f}/100")
    print(f"  Readability: {readability:.1f}/100")
    
    # Get LLM evaluation
    llm_eval = get_llm_evaluation(pr_data, review_data)
    print(f"  LLM Assessment: {llm_eval['llm_score']}/100")
    
    # Calculate composite score
    metrics = {
        'code_quality_score': code_quality,
        'test_coverage_score': test_coverage,
        'maintainability_score': maintainability,
        'readability_score': readability
    }
    
    evolution_score = calculate_evolution_score(metrics)
    
    # Adjust with LLM score (20% weight)
    final_score = int(evolution_score * 0.8 + llm_eval['llm_score'] * 0.2)
    
    print(f"\n✨ Evolution Score: {final_score}/100")
    
    # Compile results
    evaluation = {
        'evolution_score': final_score,
        'code_quality_score': code_quality,
        'test_coverage_score': test_coverage,
        'maintainability_score': maintainability,
        'readability_score': readability,
        'details': {
            'llm_assessment': llm_eval['assessment'],
            'llm_score': llm_eval['llm_score'],
            'evaluation_method': 'Custom Oumi framework with LLM assistance'
        }
    }
    
    # Save output
    with open('evaluation.json', 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    print("✓ Evaluation complete. Output: evaluation.json")


if __name__ == '__main__':
    main()
