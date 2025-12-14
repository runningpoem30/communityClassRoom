-- ========================================
-- AutoMaintainer AI - Database Schema
-- ========================================

-- Enable UUID extension for better IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====================================
-- Agent Runs Table
-- ====================================
CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    run_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    run_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    task_selected JSONB NOT NULL,
    implementation_summary TEXT,
    pr_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    error_message TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_runs_status ON agent_runs(status);
CREATE INDEX idx_agent_runs_timestamp ON agent_runs(run_timestamp DESC);

-- ====================================
-- Pull Requests Table
-- ====================================
CREATE TABLE IF NOT EXISTS pull_requests (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES agent_runs(id) ON DELETE CASCADE,
    pr_number INTEGER NOT NULL,
    pr_url TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    diff_summary TEXT,
    files_changed INTEGER DEFAULT 0,
    lines_added INTEGER DEFAULT 0,
    lines_deleted INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    merged_at TIMESTAMP,
    closed_at TIMESTAMP,
    merge_status VARCHAR(50) DEFAULT 'open'
);

CREATE INDEX idx_pull_requests_run_id ON pull_requests(run_id);
CREATE INDEX idx_pull_requests_status ON pull_requests(merge_status);
CREATE INDEX idx_pull_requests_created ON pull_requests(created_at DESC);

-- ====================================
-- Code Reviews Table (CodeRabbit)
-- ====================================
CREATE TABLE IF NOT EXISTS code_reviews (
    id SERIAL PRIMARY KEY,
    pr_id INTEGER REFERENCES pull_requests(id) ON DELETE CASCADE,
    review_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    summary TEXT,
    comments JSONB DEFAULT '[]'::jsonb,
    risk_flags JSONB DEFAULT '[]'::jsonb,
    suggestions JSONB DEFAULT '[]'::jsonb,
    security_issues INTEGER DEFAULT 0,
    performance_issues INTEGER DEFAULT 0,
    style_issues INTEGER DEFAULT 0,
    complexity_score FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_code_reviews_pr_id ON code_reviews(pr_id);

-- ====================================
-- Evaluations Table (Oumi Scores)
-- ====================================
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    pr_id INTEGER REFERENCES pull_requests(id) ON DELETE CASCADE,
    evolution_score INTEGER NOT NULL CHECK (evolution_score >= 0 AND evolution_score <= 100),
    code_quality_score FLOAT CHECK (code_quality_score >= 0 AND code_quality_score <= 100),
    test_coverage_score FLOAT CHECK (test_coverage_score >= 0 AND test_coverage_score <= 100),
    maintainability_score FLOAT CHECK (maintainability_score >= 0 AND maintainability_score <= 100),
    readability_score FLOAT CHECK (readability_score >= 0 AND readability_score <= 100),
    evaluation_details JSONB DEFAULT '{}'::jsonb,
    evaluated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evaluations_pr_id ON evaluations(pr_id);
CREATE INDEX idx_evaluations_score ON evaluations(evolution_score DESC);

-- ====================================
-- Learnings Table (Memory)
-- ====================================
CREATE TABLE IF NOT EXISTS learnings (
    id SERIAL PRIMARY KEY,
    pr_id INTEGER REFERENCES pull_requests(id) ON DELETE CASCADE,
    learning_type VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_learnings_type ON learnings(learning_type);
CREATE INDEX idx_learnings_importance ON learnings(importance_score DESC);
CREATE INDEX idx_learnings_created ON learnings(created_at DESC);

-- ====================================
-- Helper Views
-- ====================================

-- Complete run overview
CREATE OR REPLACE VIEW run_overview AS
SELECT 
    ar.id,
    ar.run_uuid,
    ar.run_timestamp,
    ar.status,
    ar.task_selected->>'title' as task_title,
    ar.task_selected->>'task_type' as task_type,
    pr.pr_number,
    pr.pr_url,
    pr.merge_status,
    pr.files_changed,
    e.evolution_score,
    e.code_quality_score,
    e.test_coverage_score,
    e.maintainability_score,
    cr.security_issues,
    cr.performance_issues,
    cr.style_issues
FROM agent_runs ar
LEFT JOIN pull_requests pr ON ar.id = pr.run_id
LEFT JOIN evaluations e ON pr.id = e.pr_id
LEFT JOIN code_reviews cr ON pr.id = cr.pr_id
ORDER BY ar.run_timestamp DESC;

-- Statistics view
CREATE OR REPLACE VIEW system_stats AS
SELECT 
    COUNT(DISTINCT ar.id) as total_runs,
    COUNT(DISTINCT pr.id) as total_prs,
    COUNT(DISTINCT CASE WHEN pr.merge_status = 'merged' THEN pr.id END) as merged_prs,
    ROUND(AVG(e.evolution_score)::numeric, 2) as avg_evolution_score,
    ROUND(AVG(e.code_quality_score)::numeric, 2) as avg_code_quality,
    ROUND(AVG(e.test_coverage_score)::numeric, 2) as avg_test_coverage,
    MAX(e.evolution_score) as best_score,
    MIN(e.evolution_score) as worst_score
FROM agent_runs ar
LEFT JOIN pull_requests pr ON ar.id = pr.run_id
LEFT JOIN evaluations e ON pr.id = e.pr_id;

-- ====================================
-- Seed Data (Optional for Demo)
-- ====================================

-- Uncomment to add demo data
-- INSERT INTO agent_runs (run_timestamp, task_selected, status) VALUES
-- (NOW() - INTERVAL '2 days', '{"title": "Fix login validation bug", "task_type": "bug_fix"}', 'success');

COMMENT ON TABLE agent_runs IS 'Each autonomous agent execution cycle';
COMMENT ON TABLE pull_requests IS 'Pull requests created by the agent';
COMMENT ON TABLE code_reviews IS 'CodeRabbit AI review results';
COMMENT ON TABLE evaluations IS 'Oumi evaluation scores and metrics';
COMMENT ON TABLE learnings IS 'Extracted insights for agent memory';
