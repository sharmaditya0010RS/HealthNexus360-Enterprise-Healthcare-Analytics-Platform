
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS governance;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS insights;
CREATE SCHEMA IF NOT EXISTS actions;
CREATE SCHEMA IF NOT EXISTS crm;
CREATE SCHEMA IF NOT EXISTS ml;

CREATE TABLE IF NOT EXISTS governance.schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pipeline_name VARCHAR(150) NOT NULL,
    source_name VARCHAR(150),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status VARCHAR(30) NOT NULL,
    records_read BIGINT NOT NULL DEFAULT 0,
    records_loaded BIGINT NOT NULL DEFAULT 0,
    error_message TEXT,
    CONSTRAINT valid_pipeline_status CHECK (
        status IN ('running', 'success', 'failed')
    ),
    CONSTRAINT valid_pipeline_counts CHECK (
        records_read >= 0 AND records_loaded >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_name_time
ON audit.pipeline_runs (pipeline_name, started_at DESC);

CREATE TABLE IF NOT EXISTS governance.data_sources (
    source_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_code VARCHAR(100) NOT NULL UNIQUE,
    source_name VARCHAR(250) NOT NULL,
    publisher VARCHAR(200) NOT NULL,
    source_url TEXT NOT NULL,
    dataset_identifier VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
