# AutoMaintainer AI - Demo Video Guide

## 🎯 What This System Does

AutoMaintainer AI is an **autonomous agent** that:
1. Analyzes a GitHub repository
2. Finds improvement opportunities (issues, TODOs, code smells)
3. Uses AI (Gemini) to implement fixes
4. Creates Pull Requests automatically
5. Gets code reviewed (CodeRabbit)
6. Learns from feedback for next time

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     KESTRA (Orchestrator)                   │
│                     http://localhost:8080                   │
│  Runs the 10-phase workflow automatically on schedule      │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌────────────┐
   │  Agent  │  │CodeRabbit│  │    Oumi    │
   │(Gemini) │  │(Reviewer)│  │(Evaluator) │
   └────┬────┘  └────┬─────┘  └─────┬──────┘
        │            │              │
        ▼            ▼              ▼
   ┌─────────────────────────────────────┐
   │        PostgreSQL Database          │
   │     (Stores runs, PRs, learnings)   │
   └─────────────────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────┐
   │     Next.js Frontend Dashboard      │
   │       http://localhost:3000         │
   │  (Shows stats, timeline, analytics) │
   └─────────────────────────────────────┘
```

---

## 📹 Demo Video Script (5-7 minutes)

### Scene 1: Introduction (30 sec)
**Show:** Your face or just the dashboard
**Say:** "AutoMaintainer AI is an autonomous agent that continuously improves code repositories without human intervention. Let me show you how it works."

### Scene 2: Dashboard Overview (1 min)
**Show:** http://localhost:3000
**Say:** 
- "This is the control center - shows all agent runs"
- "Here you can see total runs, PRs created, and Evolution Scores"
- "The timeline shows each autonomous improvement cycle"
- "Analytics shows how the agent is learning and improving over time"

### Scene 3: Kestra Workflow (1 min)
**Show:** http://localhost:8080 → Flows → automaintainer-demo
**Say:**
- "Kestra orchestrates the entire workflow"
- "The workflow has 10 phases: Clone → Analyze → Select Task → Implement → Create PR → Review → Evaluate → Store → Learn → Cleanup"
- "Let me trigger a run..."
**Action:** Click Execute → show the green checkmarks appearing

### Scene 4: Architecture Deep Dive (1.5 min)
**Show:** Code editor with the workflow YAML and Python scripts
**Say:**
- "The agent uses Gemini AI for intelligent task selection"
- "Show `agent/prompts/task-selection.md` - this is how we prompt the agent"
- "CodeRabbit automatically reviews every PR"
- "Oumi evaluates code quality with metrics"
- "Everything gets stored in PostgreSQL for the learning loop"

### Scene 5: Real Demo (1.5 min)
**Option A - Show simulation workflow running in Kestra**
**Option B - Run the Python script directly:**
```bash
python scripts/create_pr.py
```
**Show:** The actual PR being created on GitHub

### Scene 6: Learning Loop (1 min)
**Show:** Database or dashboard
**Say:**
- "Every PR result is stored"
- "The agent learns from CodeRabbit feedback"
- "Next run, it avoids previous mistakes"
- "Evolution Score trends upward over time"

### Scene 7: Conclusion (30 sec)
**Say:** 
- "AutoMaintainer AI runs 24/7 without human intervention"
- "It's not a chatbot - it's a production-grade autonomous system"
- "Thank you!"

---

## 🛠️ What to Show in Each Tool

### Kestra (http://localhost:8080)
- The workflow with 10 phases
- Execution logs showing each step
- Green checkmarks for success

### Dashboard (http://localhost:3000)
- Main page with stats (even if 0)
- Timeline page (will be empty until you have runs)
- Analytics page with charts

### GitHub
- Your test repo with a new PR created by the agent
- Show the PR description mentioning "AutoMaintainer AI"

### Code
- `workflows/main-orchestration.yml` - the workflow definition
- `agent/select_task.py` - how agent picks tasks
- `agent/prompts/task-selection.md` - the AI prompts

---

## 🎬 Quick Demo Setup

### Step 1: Make sure services are running
```bash
docker compose ps  # Should show postgres and kestra running
```

### Step 2: Open three browser tabs
1. http://localhost:3000 (Dashboard)
2. http://localhost:8080 (Kestra)
3. https://github.com/runningpoem30/serverless-graphql (Your repo)

### Step 3: In Kestra, run the demo workflow
- Shows simulation of all steps
- All green = success

### Step 4: Point to dashboard
- "Results would appear here"
- "Evolution Score tracks improvement"

---

## 💡 Key Points to Emphasize

1. **Autonomous** - No human in the loop
2. **Learning Loop** - Gets smarter over time
3. **Production-Ready** - Not just a demo
4. **Uses best tools** - Kestra, Gemini, CodeRabbit
5. **Observable** - Beautiful dashboard to monitor

---

## 🔧 Components Explained

| Component | Role | How It's Used |
|-----------|------|---------------|
| **Kestra** | Orchestrator | Runs 10-phase workflow on schedule |
| **Gemini** | AI Brain | Selects tasks, generates code |
| **CodeRabbit** | Reviewer | Reviews PRs automatically |
| **Oumi** | Evaluator | Calculates quality scores |
| **PostgreSQL** | Memory | Stores runs, learns patterns |
| **Next.js** | Dashboard | Visualizes everything |

---

## ⚠️ For Your Video

The **demo workflow** (`automaintainer-demo`) shows the SIMULATION.

The **real workflow** would actually create PRs but requires:
- Docker-in-Docker access (complex setup)
- Or running Python scripts directly

**For your video, the simulation is perfect** - it shows how the system works conceptually. Emphasize that "in production, each step calls real APIs and creates real PRs."
