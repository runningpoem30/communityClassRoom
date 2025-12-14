"""
AutoMaintainer AI - Memory Manager
Handles all database operations for storing and retrieving agent memory.
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional


class MemoryManager:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def test_connection(self):
        """Test database connectivity"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.close()
            print("✓ Database connection successful")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    # =============================================
    # CREATE OPERATIONS
    # =============================================
    
    def create_agent_run(self, task_selected: Dict) -> int:
        """Create new agent run record"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agent_runs (run_timestamp, task_selected, status)
                    VALUES (NOW(), %s, 'in_progress')
                    RETURNING id
                """, (json.dumps(task_selected),))
                run_id = cur.fetchone()[0]
                conn.commit()
                return run_id
        finally:
            conn.close()
    
    def create_pull_request(self, run_id: int, pr_data: Dict) -> int:
        """Create pull request record"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pull_requests 
                    (run_id, pr_number, pr_url, title, description, files_changed, 
                     lines_added, lines_deleted, merge_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    run_id,
                    pr_data.get('number'),
                    pr_data.get('url'),
                    pr_data.get('title'),
                    pr_data.get('description'),
                    pr_data.get('files_changed', 0),
                    pr_data.get('lines_added', 0),
                    pr_data.get('lines_deleted', 0),
                    pr_data.get('status', 'open')
                ))
                pr_id = cur.fetchone()[0]
                conn.commit()
                return pr_id
        finally:
            conn.close()
    
    def create_code_review(self, pr_id: int, review_data: Dict) -> int:
        """Store CodeRabbit review"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO code_reviews
                    (pr_id, summary, comments, risk_flags, suggestions,
                     security_issues, performance_issues, style_issues, complexity_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    pr_id,
                    review_data.get('summary'),
                    json.dumps(review_data.get('comments', [])),
                    json.dumps(review_data.get('risk_flags', [])),
                    json.dumps(review_data.get('suggestions', [])),
                    review_data.get('security_issues', 0),
                    review_data.get('performance_issues', 0),
                    review_data.get('style_issues', 0),
                    review_data.get('complexity_score')
                ))
                review_id = cur.fetchone()[0]
                conn.commit()
                return review_id
        finally:
            conn.close()
    
    def create_evaluation(self, pr_id: int, eval_data: Dict) -> int:
        """Store Oumi evaluation"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO evaluations
                    (pr_id, evolution_score, code_quality_score, test_coverage_score,
                     maintainability_score, readability_score, evaluation_details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    pr_id,
                    eval_data.get('evolution_score'),
                    eval_data.get('code_quality_score'),
                    eval_data.get('test_coverage_score'),
                    eval_data.get('maintainability_score'),
                    eval_data.get('readability_score'),
                    json.dumps(eval_data.get('details', {}))
                ))
                eval_id = cur.fetchone()[0]
                conn.commit()
                return eval_id
        finally:
            conn.close()
    
    def create_learning(self, pr_id: int, learning: Dict) -> int:
        """Store a learning insight"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO learnings
                    (pr_id, learning_type, summary, context, importance_score)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    pr_id,
                    learning.get('type'),
                    learning.get('summary'),
                    json.dumps(learning.get('context', {})),
                    learning.get('importance', 0.5)
                ))
                learning_id = cur.fetchone()[0]
                conn.commit()
                return learning_id
        finally:
            conn.close()
    
    # =============================================
    # READ OPERATIONS
    # =============================================
    
    def get_past_prs(self, limit: int = 10) -> List[Dict]:
        """Get recent PR history"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM run_overview
                    ORDER BY run_timestamp DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_learnings(self, limit: int = 20, min_importance: float = 0.3) -> List[Dict]:
        """Get relevant learnings for context"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT l.*, pr.title as pr_title
                    FROM learnings l
                    LEFT JOIN pull_requests pr ON l.pr_id = pr.id
                    WHERE l.importance_score >= %s
                    ORDER BY l.importance_score DESC, l.created_at DESC
                    LIMIT %s
                """, (min_importance, limit))
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_negative_feedback(self, limit: int = 10) -> List[Dict]:
        """Get learnings from failed/low-scoring PRs"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT l.summary, l.context, e.evolution_score, pr.title
                    FROM learnings l
                    JOIN pull_requests pr ON l.pr_id = pr.id
                    JOIN evaluations e ON pr.id = e.pr_id
                    WHERE l.learning_type IN ('mistake', 'anti_pattern')
                       OR e.evolution_score < 60
                    ORDER BY l.created_at DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM system_stats")
                result = cur.fetchone()
                return dict(result) if result else {}
        finally:
            conn.close()
    
    # =============================================
    # UPDATE OPERATIONS
    # =============================================
    
    def update_run_status(self, run_id: int, status: str, 
                         summary: Optional[str] = None, pr_url: Optional[str] = None):
        """Update agent run status"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agent_runs
                    SET status = %s,
                        implementation_summary = COALESCE(%s, implementation_summary),
                        pr_url = COALESCE(%s, pr_url),
                        updated_at = NOW()
                    WHERE id = %s
                """, (status, summary, pr_url, run_id))
                conn.commit()
        finally:
            conn.close()
    
    def update_pr_status(self, pr_id: int, merge_status: str, merged_at: Optional[datetime] = None):
        """Update PR merge status"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE pull_requests
                    SET merge_status = %s,
                        merged_at = %s
                    WHERE id = %s
                """, (merge_status, merged_at, pr_id))
                conn.commit()
        finally:
            conn.close()
