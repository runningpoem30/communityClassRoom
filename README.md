# AutoMaintainer AI

> **A production-grade autonomous agent system that continuously improves open-source repositories without human intervention.**

![System Architecture](https://img.shields.io/badge/Agent-Cline-blue) ![Orchestration](https://img.shields.io/badge/Orchestration-Kestra-green) ![Review](https://img.shields.io/badge/Review-CodeRabbit-purple) ![Evaluation](https://img.shields.io/badge/Evaluation-Oumi-orange)

---

## 🎯 What is AutoMaintainer AI?

AutoMaintainer AI is **not a chatbot**. It's a real agentic software system that:

1. **Analyzes** a GitHub repository autonomously
2. **Selects** exactly ONE meaningful improvement task per run
3. **Implements** the change using an autonomous coding agent (Cline)
4. **Opens** a pull request with clear reasoning
5. **Reviews** the PR using AI code review (CodeRabbit)
6. **Evaluates** quality with custom metrics (Oumi framework)
7. **Learns** from feedback to improve future runs
8. **Visualizes** its evolution over time on a live dashboard

---

## 🏗️ System Architecture

```
┌─────────────┐
│   Kestra    │  ← Orchestrates entire lifecycle
│  (Workflow) │
└──────┬──────┘
       │
       ├──► Clone Repo
       ├──► Analyze Context (issues, TODOs, structure)
       │
       ├──► 🧠 Cline Agent
       │    ├─ Select ONE task
       │    ├─ Implement change
       │    └─ Write tests
       │
       ├──► Create Pull Request (GitHub)
       │
       ├──► 🐰 CodeRabbit Review
       │    └─ Analyze code quality, risks, suggestions
       │
       ├──► 🎯 Oumi Evaluation
       │    └─ Calculate Evolution Score (0-100)
       │
       ├──► 💾 Store Results (PostgreSQL)
       │    └─ Learning memory for future runs
       │
       └──► 📊 Update Dashboard (Next.js)
```

---

## 📁 Project Structure

```
aiagentsassemble/
├── agent/                    # Autonomous coding agent
│   ├── prompts/             # Task selection, implementation, reflection
│   ├── select_task.py       # LLM-based task selection
│   └── executor.py          # Cline integration
│
├── workflows/               # Kestra workflows
│   └── main-orchestration.yml  # Complete lifecycle orchestration
│
├── evaluation/             # Quality assessment
│   ├── oumi_evaluator.py   # Custom evaluation metrics
│   └── coderabbit_integration.py
│
├── memory/                 # Persistent learning
│   ├── schema.sql         # PostgreSQL database schema
│   ├── memory_manager.py  # CRUD operations
│   └── retrieve_learnings.py
│
├── frontend/              # Next.js dashboard
│   ├── app/
│   │   ├── page.tsx      # Landing page with live stats
│   │   ├── timeline/     # Chronological run history
│   │   ├── analytics/    # Charts and trends
│   │   └── api/data/     # API endpoint
│   └── lib/db.ts         # PostgreSQL connection
│
├── scripts/
│   └── setup.sh          # One-command setup
│
├── docker-compose.yml    # PostgreSQL + Kestra
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (for PostgreSQL + Kestra)
- **Node.js 18+** (for frontend)
- **Python 3.11+** (for agent scripts)
- **API Keys**:
  - Anthropic (Claude) or OpenAI (GPT-4) for Cline
  - GitHub Personal Access Token
  - CodeRabbit API Key (optional)

### Setup (5 minutes)

```bash
# 1. Clone the repository
cd aiagentsassemble

# 2. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# 3. Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 4. Start the frontend
cd frontend
npm run dev
```

### Access Points

- **Dashboard**: http://localhost:3000
- **Kestra UI**: http://localhost:8080
- **API**: http://localhost:3000/api/data

---

## 🎮 Running the System

### Option 1: Manual Trigger (Kestra UI)

1. Open http://localhost:8080
2. Navigate to **Flows** → `automaintainer.main-orchestration`
3. Click **Execute**
4. Monitor progress in **Executions** tab
5. View results in dashboard at http://localhost:3000

### Option 2: Scheduled Runs

The workflow automatically runs daily at 2 AM (configurable in `workflows/main-orchestration.yml`).

### Option 3: API Trigger

```bash
curl -X POST http://localhost:8080/api/v1/executions/automaintainer/main-orchestration \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"manual_trigger": true}}'
```

---

## 📊 Dashboard Features

### Landing Page
- **Live Stats**: Total runs, PRs created, merge rate, average score
- **System Architecture**: Visual component overview
- **Quick Navigation**: Timeline, Analytics, API access

### Timeline
- Chronological history of all agent runs
- Task details with type badges (bug fix, feature, refactor, etc.)
- Evolution scores with color coding (green ≥80, yellow ≥60, red <60)
- PR links and merge status
- CodeRabbit issue counts (security, performance, style)

### Analytics
- **Evolution Score Trend**: Line chart showing improvement over time
- **Task Type Distribution**: Pie chart of work categories
- **Key Metrics**: Success rate, average score, best/worst scores
- **Code Quality Trends**: Maintainability, readability, test coverage

---

## 🧠 Agent Intelligence

### Task Selection Process

The agent uses LLM reasoning to select tasks based on:

1. **Impact**: High value to maintainers/users
2. **Scope**: Completable in one PR
3. **Safety**: Low breaking-change risk
4. **Testability**: Can be verified
5. **Novelty**: Not duplicate work

**Selection Sources**:
- Open GitHub issues
-TODO comments in code
- Past PR learnings (what worked, what didn't)
- Code quality analysis

### Learning Loop

Every PR generates learnings stored in PostgreSQL:

```sql
learnings
├── success_patterns  (repeat these)
├── mistakes          (avoid these)
├── best_practices    (from high-scoring PRs)
└── anti_patterns     (from low-scoring PRs)
```

Future runs retrieve these learnings as context, enabling **continuous improvement**.

---

## 🎯 Evaluation System (Oumi Framework)

Each PR receives an **Evolution Score** (0-100) based on:

| Metric | Weight | Measures |
|--------|--------|----------|
| **Code Quality** | 30% | Complexity, naming, structure |
| **Test Coverage** | 25% | Tests added, edge cases |
| **Maintainability** | 25% | Long-term impact, tech debt |
| **Readability** | 20% | Documentation, clarity |

**Additional Factors**:
- CodeRabbit review flags (security, performance, style)
- LLM qualitative assessment
- Historical performance

---

## 🔧 Configuration

### Environment Variables

```bash
# LLM for agent
ANTHROPIC_API_KEY=sk-ant-...
CLINE_MODEL=claude-3-5-sonnet-20241022

# GitHub integration
GITHUB_TOKEN=ghp_...
GITHUB_REPO_OWNER=your-username
GITHUB_TARGET_REPO=demo-repo

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/automaintainer

# Code review
CODERABBIT_API_KEY=your-coderabbit-key

# Evaluation
OUMI_API_KEY=sk-...  # OpenAI for evaluation LLM
OUMI_MODEL=gpt-4
```

### Workflow Customization

Edit `workflows/main-orchestration.yml` to:
- Change schedule (cron expression)
- Adjust timeouts
- Add custom steps
- Modify retry logic

---

## 📈 Demo Flow

**For Judges**: Here's a complete walkthrough:

1. **Setup** (5 min): Run `./scripts/setup.sh`
2. **Configure**: Add API keys to `.env`
3. **Start Services**: `docker-compose up -d`
4. **Start Frontend**: `cd frontend && npm run dev`
5. **Trigger Run**: Execute workflow in Kestra UI (http://localhost:8080)
6. **Monitor**: Watch Kestra execution logs
7. **View Results**: Check dashboard (http://localhost:3000)

**Expected Timeline** (per run):
- Clone & analyze: 1-2 min
- Task selection: 30 sec
- Implementation: 5-15 min (depends on task)
- PR creation: 10 sec
- CodeRabbit review: 2-5 min
- Evaluation: 30 sec
- **Total**: ~10-25 minutes per improvement

---

## 🏆 Key Differentiators

### Why This is Production-Grade

✅ **Observable**: Every step logged and traceable in Kestra
✅ **Retry-Safe**: Idempotent workflows with error handling
✅ **Persistent Memory**: PostgreSQL for audit trail and learning
✅ **Real PRs**: Not mocked - actual GitHub pull requests
✅ **Feedback Loop**: CodeRabbit + Oumi → Learning → Better future runs
✅ **Scalable**: Docker + Kestra handles high volume
✅ **Judge-Ready**: Clean frontend, clear architecture, real demo

### Not a Toy Demo

- ❌ No hardcoded data
- ❌ No fake PRs
- ❌ No manual intervention required
- ✅ Truly autonomous operation
- ✅ Real learning and improvement
- ✅ Production-ready infrastructure

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd memory && pytest tests/
cd ../evaluation && pytest tests/
cd ../agent && pytest tests/

# Frontend tests
cd frontend && npm test
```

### Adding Custom Evaluation Metrics

Edit `evaluation/oumi_evaluator.py` and add your metric function:

```python
def evaluate_custom_metric(pr_data: Dict) -> float:
    # Your logic here
    return score  # 0-100
```

### Extending the Learning Loop

Add custom learning types in `memory/schema.sql`:

```sql
INSERT INTO learnings (pr_id, learning_type, summary, importance_score)
VALUES (%s, 'custom_pattern', %s, 0.8);
```

---

## 📜 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Agent** | Cline (Claude/GPT-4) | Autonomous code implementation |
| **Orchestration** | Kestra | Workflow scheduling & coordination |
| **Code Review** | CodeRabbit | AI-powered PR review |
| **Evaluation** | Custom Oumi | Code quality scoring |
| **Database** | PostgreSQL | Memory & results storage |
| **Frontend** | Next.js 14 + TypeScript | Dashboard UI |
| **Styling** | Tailwind CSS | Modern, responsive design |
| **Charts** | Recharts | Analytics visualizations |
| **Deployment** | Docker Compose | Local orchestration |

---

## 🐛 Troubleshooting

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart
```

### Kestra Workflow Not Found

```bash
# Upload workflow manually
curl -X POST http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  --data-binary @workflows/main-orchestration.yml
```

### Frontend API Errors

- Ensure `DATABASE_URL` in `frontend/.env.local` matches Docker setup
- Check PostgreSQL logs: `docker-compose logs postgres`

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 👥 Credits

Built for the **AI Agents Hackathon** by demonstrating production-grade autonomous systems.

**Technologies**:
- [Cline](https://github.com/cline/cline) - Autonomous coding agent
- [Kestra](https://kestra.io) - Workflow orchestration
- [CodeRabbit](https://coderabbit.ai) - AI code review
- [Next.js](https://nextjs.org) - React framework
- [PostgreSQL](https://postgresql.org) - Database

---

## 🚀 Future Enhancements

- [ ] Multi-repository support
- [ ] Slack/Discord notifications
- [ ] A/B testing different LLM models
- [ ] Advanced learning algorithms (RL)
- [ ] Cost tracking and optimization
- [ ] Self-healing on test failures
- [ ] Deployment to production (Vercel + cloud DB)

---

**Built with precision. Engineered for judges.**

For questions or demo requests, see the documentation in `/docs`.
