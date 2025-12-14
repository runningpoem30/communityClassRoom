You are an autonomous agent learning from feedback on your recent pull request.

## Pull Request Details
- **Title**: {pr_title}
- **Task Type**: {task_type}
- **Files Changed**: {files_changed}
- **Status**: {merge_status}

## Evaluation Data

### CodeRabbit Review
{coderabbit_summary}

**Key Comments**:
{coderabbit_comments}

**Risk Flags**:
{risk_flags}

**Suggestions**:
{suggestions}

### Oumi Evolution Score: {evolution_score}/100
- **Code Quality**: {code_quality_score}/100
- **Test Coverage**: {test_coverage_score}/100
- **Maintainability**: {maintainability_score}/100
- **Readability**: {readability_score}/100

### Merge Outcome
- **Status**: {merge_status} (merged | rejected | pending)
- **Merge Time**: {merge_time}

## Reflection Questions

### 1. What Went Well?
Identify the positive aspects of this PR:
- Technical decisions that worked well
- Patterns worth repeating
- Effective testing strategies
- Good architectural choices

### 2. What Could Be Improved?
Analyze areas for improvement:
- Code quality issues raised by CodeRabbit
- Missing test coverage
- Unclear or complex code
- Documentation gaps
- Overlooked edge cases

### 3. What Patterns Should You Avoid?
Extract anti-patterns from this experience:
- Common mistakes made
- Assumptions that were wrong
- Approaches that led to issues
- Style violations

### 4. What Patterns Should You Repeat?
Extract best practices from this experience:
- Successful problem-solving approaches
- Effective testing strategies
- Good code organization
- Clear documentation practices

## Output Format (JSON)

```json
{
  "success_patterns": [
    "Specific pattern to repeat in future (e.g., 'Added edge case tests before implementation')"
  ],
  "mistakes_to_avoid": [
    "Specific mistake to avoid (e.g., 'Forgot to handle null values in input validation')"
  ],
  "key_learnings": [
    "Important insight (e.g., 'Always check for concurrent access in shared resources')"
  ],
  "improvement_areas": [
    "Area needing focus (e.g., 'Test coverage for error conditions')"
  ],
  "overall_summary": "2-3 sentence summary of the main takeaway from this PR experience",
  "confidence_level": "high|medium|low",
  "recommended_focus_next_time": "Specific area to prioritize in next PR (e.g., 'Focus on comprehensive error handling')"
}
```

## Analysis Guidelines

### Be Specific
❌ "Code quality was good"
✅ "Breaking complex function into smaller helper functions improved readability"

### Be Actionable
❌ "Tests need improvement"
✅ "Add edge case tests for empty input and boundary conditions before coding"

### Be Honest
- If score is low, identify concrete reasons
- If CodeRabbit flagged issues, acknowledge and learn
- If tests were insufficient, commit to better coverage

### Connect Feedback to Future Action
- CodeRabbit: "Complexity too high" → Future: "Limit functions to <50 lines, extract helpers"
- Oumi: "Low test coverage" → Future: "Write tests before implementation (TDD)"
- Merged successfully → Future: "Repeat this level of thoroughness"

## Examples

### Example: High-Scoring PR (90/100, Merged)
```json
{
  "success_patterns": [
    "Wrote comprehensive tests covering all edge cases before implementation",
    "Added inline comments explaining complex algorithm logic",
    "Broke down large function into smaller, testable units"
  ],
  "mistakes_to_avoid": [],
  "key_learnings": [
    "TDD approach caught edge cases early, preventing bugs",
    "Small, focused functions are easier to test and review"
  ],
  "improvement_areas": [
    "Could have added performance benchmarks for optimization changes"
  ],
  "overall_summary": "Well-executed bug fix with excellent test coverage. Reviewers appreciated clear code structure and thorough testing. Minor improvement: add performance metrics for future optimizations.",
  "confidence_level": "high",
  "recommended_focus_next_time": "Maintain current testing rigor, add performance validation"
}
```

### Example: Low-Scoring PR (45/100, Issues Found)
```json
{
  "success_patterns": [
    "Correctly identified the root cause of the bug"
  ],
  "mistakes_to_avoid": [
    "Made changes without understanding full context, broke related feature",
    "Skipped writing tests, leading to undetected edge case failures",
    "Used poor variable names making code hard to follow"
  ],
  "key_learnings": [
    "Always run full test suite before creating PR",
    "Read related code before making changes to understand dependencies",
    "Invest time in clear naming - it helps reviewers and future maintainers"
  ],
  "improvement_areas": [
    "Test coverage - write tests first",
    "Code readability - use descriptive names",
    "Impact analysis - trace dependencies before changing"
  ],
  "overall_summary": "Fix targeted right problem but lacked proper testing and broke related functionality. CodeRabbit flagged variable naming and missing error handling. Key lesson: comprehensive testing and impact analysis are non-negotiable.",
  "confidence_level": "medium",
  "recommended_focus_next_time": "Test-driven development and thorough dependency analysis"
}
```

## Instructions
1. Review ALL feedback data provided above
2. Be brutally honest in self-assessment
3. Extract concrete, actionable learnings
4. Format output as JSON following the structure exactly
5. Keep overall_summary concise (max 3 sentences)

**Your future performance depends on learning from this experience. Reflect deeply.**
