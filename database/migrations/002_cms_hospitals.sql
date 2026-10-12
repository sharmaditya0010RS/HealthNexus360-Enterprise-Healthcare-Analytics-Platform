
CREATE TABLE IF NOT EXISTS raw.cms_hospital_snapshots (
    snapshot_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_url TEXT NOT NULL,
    source_sha256 CHAR(64) NOT NULL UNIQUE,
    downloaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_row_count INTEGER NOT NULL CHECK (source_row_count > 0),
    source_column_count INTEGER NOT NULL CHECK (source_column_count > 0)
);

CREATE TABLE IF NOT EXISTS raw.cms_hospital_records (
    snapshot_id BIGINT NOT NULL
        REFERENCES raw.cms_hospital_snapshots(snapshot_id),
    row_number INTEGER NOT NULL CHECK (row_number > 0),
    record JSONB NOT NULL,
    PRIMARY KEY (snapshot_id, row_number)
);

CREATE TABLE IF NOT EXISTS core.hospitals (
    snapshot_id BIGINT NOT NULL
        REFERENCES raw.cms_hospital_snapshots(snapshot_id),
    facility_id VARCHAR(20) NOT NULL,
    facility_name TEXT NOT NULL,
    state VARCHAR(10) NOT NULL,
    city TEXT,
    zip_code VARCHAR(15),
    hospital_type TEXT,
    hospital_ownership TEXT,
    emergency_services BOOLEAN,
    overall_rating SMALLINT,
    PRIMARY KEY (snapshot_id, facility_id),
    CONSTRAINT hospital_rating_range CHECK (
        overall_rating BETWEEN 1 AND 5
    )
);

CREATE INDEX IF NOT EXISTS idx_hospitals_state
ON core.hospitals (snapshot_id, state);

CREATE OR REPLACE VIEW mart.hospital_overview AS
WITH latest AS (
    SELECT snapshot_id
    FROM raw.cms_hospital_snapshots
    ORDER BY downloaded_at DESC, snapshot_id DESC
    LIMIT 1
)
SELECT
    h.snapshot_id,
    COUNT(*) AS hospital_count,
    COUNT(h.overall_rating) AS rated_hospitals,
    COUNT(DISTINCT h.state) AS state_count,
    COUNT(*) FILTER (
        WHERE h.emergency_services IS TRUE
    ) AS emergency_service_hospitals,
    ROUND(AVG(h.overall_rating), 2) AS average_rating
FROM core.hospitals h
JOIN latest l ON h.snapshot_id = l.snapshot_id
GROUP BY h.snapshot_id;
