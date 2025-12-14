# System Design Document

## AutoMaintainer AI - Technical Architecture

### Overview
AutoMaintainer AI is a production-grade autonomous agent system built for continuous repository improvement. This document provides technical details for implementation and deployment.

## Core Components

### 1. Workflow Orchestration (Kestra)

**Purpose**: Coordinate the entire improvement lifecycle from task selection to learning.

**Key Workflows**:
- `main-orchestration.yml`: Complete 10-phase lifecycle
- Scheduled: Daily at 2 AM (configurable)
- Manual trigger: Available via UI or API

**Phases**:
1. Setup & Clone
2. Context Gathering
3. Task Selection (LLM)
4. Implementation (Cline)
5. PR Creation (GitHub)
6. Code Review (CodeRabbit)
7. Evaluation (Oumi)
8. Persistence (PostgreSQL)
9. Learning & Reflection
10. Cleanup

### 2. Autonomous Agent (Cline Integration)

**Architecture**: LLM-powered agent with structured prompts

**Prompts**:
- `task-selection.md`: Analyzes repo and selects ONE task
- `implementation.md`: Implements change with tests
- `reflection.md`: Learns from PR feedback

**Models Supported**:
- Claude 3.5 Sonnet (recommended)
- GPT-4
- Custom via MCP

**Execution**: Python scripts invoke LLM with context:
```python
# select_task.py
context = format_context(analysis, issues, learnings)
task = select_task_with_llm(context, model="claude-3-5-sonnet")
```

### 3. Memory & Learning (PostgreSQL)

**Schema**: 5 core tables
- `agent_runs`: Each execution cycle
- `pull_requests`: PR metadata
- `code_reviews`: CodeRabbit results
- `evaluations`: Oumi scores
- `learnings`: Extracted insights

**Learning Loop**:
1. Store PR feedback
2. Extract patterns (success/mistakes)
3. Retrieve for next run context
4. Continuous improvement

**Views**:
- `run_overview`: Complete run history
- `system_stats`: Aggregate metrics

### 4. Evaluation System (Oumi Framework)

**Custom Metrics**:
```python
evolution_score = weighted_average([
    code_quality * 0.30,
    test_coverage * 0.25,
    maintainability * 0.25,
    readability * 0.20
])
```

**Inputs**:
- PR diff analysis
- CodeRabbit review
- LLM qualitative assessment

**Output**: 0-100 score with breakdown

### 5. Code Review (CodeRabbit)

**Integration**: GitHub webhook + API
- Automatic review on PR creation
- Fetches results via API
- Stores: comments, risk flags, issues

**Metrics Tracked**:
- Security issues
- Performance issues
- Style violations
- Complexity score

### 6. Frontend Dashboard (Next.js)

**Technology Stack**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts (analytics)
- PostgreSQL (direct connection)

**Pages**:
1. `/` - Landing with live stats
2. `/timeline` - Chronological run history
3. `/analytics` - Charts and trends
4. `/api/data` - JSON API endpoint

**Design Philosophy**:
- Dark mode gradient design
- Real-time data (no caching)
- Responsive & fast
- Production-ready

## Data Flow

```
User/Scheduler
    ↓
Kestra Trigger
    ↓
Clone Repo → Analyze → Fetch Issues
    ↓
Retrieve Past Learnings (PostgreSQL)
    ↓
LLM Task Selection (Cline)
    ↓
LLM Implementation (Cline)
    ↓
Git Commit + Push
    ↓
Create GitHub PR
    ↓
CodeRabbit Review (async)
    ↓
Oumi Evaluation
    ↓
Store Results (PostgreSQL)
    ↓
Extract Learnings
    ↓
Update Dashboard
```

## Deployment Architecture

### Local Development
```
Docker Compose:
├── PostgreSQL (port 5432)
├── Kestra (port 8080)
└── Next.js Dev Server (port 3000)
```

### Production (Future)
```
Vercel (Frontend)
    ↓
Cloud PostgreSQL (Supabase/Neon)
    ↓
Kestra Cloud
    ↓
GitHub Actions (CI/CD)
```

## Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **Database**: Connection pooling with SSL in production
3. **GitHub Token**: Minimal required permissions
4. **PR Validation**: All changes reviewed before merge

## Performance Optimizations

1. **Database**:
   - Indexed columns for fast queries
   - Connection pooling (max 20)
   - Materialized views for stats

2. **Frontend**:
   - Server-side rendering
   - API route caching where appropriate
   - Lazy loading charts

3. **Workflows**:
   - Parallel task execution where possible
   - Timeout protection
   - Retry logic for transient failures

## Monitoring & Observability

### Kestra UI
- Real-time execution logs
- Task status tracking
- Error reporting

### Frontend
- System stats dashboard
- Score trend visualization
- Run timeline

### Database
- Audit trail in `agent_runs`
- Error logging table
- Performance metrics

## Testing Strategy

### Unit Tests
- `memory_manager.py`: Database operations
- `oumi_evaluator.py`: Scoring logic
- `select_task.py`: LLM integration

### Integration Tests
- Full Kestra workflow execution
- Database read/write cycle
- Frontend API routes

### E2E Tests
- Complete run from trigger to dashboard update

## Configuration Management

### Environment Variables
- Development: `.env.local`
- Production: Platform-specific (Vercel, Docker)
- Secrets: Never committed to git

### Workflow Configuration
- YAML files in `/workflows`
- Version controlled
- Validated before deployment

## Scalability Considerations

### Current Capacity
- Handles 10-20 runs per day
- Supports single repository

### Future Scaling
- Multi-repository support
- Distributed Kestra cluster
- Read replicas for database
- CDN for frontend

## Error Handling

### Workflow Level
```yaml
errors:
  - id: error_handler
    type: log_error
```

### Application Level
- Try-catch in Python scripts
- Graceful degradation
- Error persistence in DB

## Maintenance

### Regular Tasks
- Database backups (automated)
- Log rotation
- Dependency updates
- API key rotation

### Monitoring
- Kestra execution failures
- Database growth
- API rate limits
- Frontend uptime

## Future Enhancements

1. **Advanced Learning**:
   - Reinforcement learning from merge outcomes
   - Pattern recognition in successful PRs

2. **Multi-Repository**:
   - Support multiple target repos
   - Prioritization algorithm

3. **Notifications**:
   - Slack/Discord integration
   - Email reports

4. **Analytics**:
   - Cost tracking per run
   - ROI calculation

5. **Self-Healing**:
   - Automatic rollback on test failures
   - Auto-retry failed runs

---

**Document Version**: 1.0
**Last Updated**: 2025-12-14
**Maintainer**: AutoMaintainer AI Team
