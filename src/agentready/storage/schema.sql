-- SQLite Database Schema for Quality Profiling and Benchmarking
-- Version: 1.0.0
-- Created: 2026-01-28

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    repo_url TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    primary_language TEXT,
    last_assessed DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id TEXT PRIMARY KEY,
    repo_url TEXT NOT NULL,
    overall_score REAL NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    metadata TEXT,
    FOREIGN KEY (repo_url) REFERENCES repositories(repo_url) ON DELETE CASCADE
);

-- Assessment metadata table
CREATE TABLE IF NOT EXISTS assessment_metadata (
    assessment_id TEXT PRIMARY KEY,
    commit_count INTEGER,
    head_commit_sha TEXT NOT NULL,
    file_count INTEGER NOT NULL CHECK (file_count >= 0),
    line_count INTEGER NOT NULL CHECK (line_count >= 0),
    languages TEXT NOT NULL,
    contributor_count INTEGER,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
);

-- Assessor results table
CREATE TABLE IF NOT EXISTS assessor_results (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    assessor_name TEXT NOT NULL,
    score REAL NOT NULL CHECK (score >= 0 AND score <= 100),
    metrics TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'skipped')),
    executed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    UNIQUE (assessment_id, assessor_name)
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,
    assessor_result_id TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('testing', 'documentation', 'security', 'code_quality', 'ecosystem', 'maintainability')),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    description TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (assessor_result_id) REFERENCES assessor_results(id) ON DELETE CASCADE
);

-- Benchmark snapshots table
CREATE TABLE IF NOT EXISTS benchmark_snapshots (
    id TEXT PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    repository_count INTEGER NOT NULL CHECK (repository_count > 0),
    statistical_summary TEXT NOT NULL
);

-- Benchmark rankings table
CREATE TABLE IF NOT EXISTS benchmark_rankings (
    id TEXT PRIMARY KEY,
    benchmark_snapshot_id TEXT NOT NULL,
    repo_url TEXT NOT NULL,
    rank INTEGER NOT NULL CHECK (rank > 0),
    percentile REAL NOT NULL CHECK (percentile >= 0 AND percentile <= 100),
    dimension_scores TEXT NOT NULL,
    FOREIGN KEY (benchmark_snapshot_id) REFERENCES benchmark_snapshots(id) ON DELETE CASCADE,
    FOREIGN KEY (repo_url) REFERENCES repositories(repo_url) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_assessments_repo_url ON assessments(repo_url);
CREATE INDEX IF NOT EXISTS idx_assessments_repo_started ON assessments(repo_url, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_assessor_results_assessment ON assessor_results(assessment_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_assessor_result ON recommendations(assessor_result_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_severity ON recommendations(severity);
CREATE INDEX IF NOT EXISTS idx_benchmark_rankings_snapshot ON benchmark_rankings(benchmark_snapshot_id, rank);
CREATE INDEX IF NOT EXISTS idx_repositories_last_assessed ON repositories(last_assessed);
