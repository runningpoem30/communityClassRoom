"""
AutoMaintainer AI - Repository Analyzer
Analyzes repository structure, finds TODOs, and extracts context.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict


def analyze_structure(repo_path: str) -> Dict:
    """Analyze repository structure"""
    structure = {
        'total_files': 0,
        'total_lines': 0,
        'file_types': {},
        'directories': []
    }
    
    for root, dirs, files in os.walk(repo_path):
        # Skip common ignored directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.next']]
        
        rel_path = os.path.relpath(root, repo_path)
        if rel_path != '.':
            structure['directories'].append(rel_path)
        
        for file in files:
            structure['total_files'] += 1
            ext = Path(file).suffix
            structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
            
            # Count lines
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    structure['total_lines'] += lines
            except:
                pass
    
    return structure


def find_todos(repo_path: str) -> List[Dict]:
    """Find TODO comments in code"""
    todos = []
    
    code_extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rb', '.php', '.md']
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.next']]
        
        for file in files:
            if not any(file.endswith(ext) for ext in code_extensions):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if 'TODO' in line or 'FIXME' in line or 'HACK' in line:
                            todos.append({
                                'file': rel_path,
                                'line': line_num,
                                'text': line.strip()[:100]  # Limit length
                            })
            except:
                pass
    
    return todos[:50]  # Limit to first 50


def main():
    parser = argparse.ArgumentParser(description='Analyze repository')
    parser.add_argument('repo_path', help='Path to repository')
    args = parser.parse_args()
    
    print(f"🔍 Analyzing repository: {args.repo_path}")
    
    # Get repo name
    repo_name = os.path.basename(os.path.abspath(args.repo_path))
    
    # Analyze structure
    structure = analyze_structure(args.repo_path)
    print(f"  Files: {structure['total_files']}, Lines: {structure['total_lines']}")
    
    # Find TODOs
    todos = find_todos(args.repo_path)
    print(f"  TODOs found: {len(todos)}")
    
    # Compile analysis
    analysis = {
        'repo_name': repo_name,
        'structure': structure,
        'todos': todos
    }
    
    # Save output
    with open('analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print("✓ Analysis complete. Output: analysis.json")


if __name__ == '__main__':
    main()
