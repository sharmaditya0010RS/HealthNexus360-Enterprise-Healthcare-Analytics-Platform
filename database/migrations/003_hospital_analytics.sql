
CREATE OR REPLACE VIEW mart.hospital_latest AS
WITH latest AS (
    SELECT snapshot_id
    FROM raw.cms_hospital_snapshots
    ORDER BY downloaded_at DESC, snapshot_id DESC
    LIMIT 1
)
SELECT
    h.snapshot_id,
    h.facility_id,
    h.facility_name,
    h.state,
    h.city,
    h.zip_code,
    h.hospital_type,
    h.hospital_ownership,
    h.emergency_services,
    h.overall_rating
FROM core.hospitals h
JOIN latest l
    ON h.snapshot_id = l.snapshot_id;

CREATE OR REPLACE VIEW mart.hospital_state_summary AS
SELECT
    state,
    COUNT(*)::BIGINT AS hospital_count,
    COUNT(overall_rating)::BIGINT AS rated_hospitals,
    COUNT(*) FILTER (
        WHERE overall_rating IS NULL
    )::BIGINT AS unrated_hospitals,
    COUNT(*) FILTER (
        WHERE emergency_services IS TRUE
    )::BIGINT AS emergency_hospitals,
    COUNT(*) FILTER (
        WHERE emergency_services IS NULL
    )::BIGINT AS emergency_unknown_hospitals,
    ROUND(
        100.0 * COUNT(overall_rating)
        / NULLIF(COUNT(*), 0),
        2
    ) AS rating_coverage_pct,
    ROUND(
        AVG(overall_rating)::NUMERIC,
        2
    ) AS average_reported_rating
FROM mart.hospital_latest
GROUP BY state;

CREATE OR REPLACE VIEW mart.hospital_rating_distribution AS
SELECT
    overall_rating,
    COUNT(*)::BIGINT AS hospital_count
FROM mart.hospital_latest
GROUP BY overall_rating;

CREATE OR REPLACE VIEW mart.hospital_data_quality AS
WITH latest AS (
    SELECT
        snapshot_id,
        source_row_count,
        downloaded_at,
        source_sha256
    FROM raw.cms_hospital_snapshots
    ORDER BY downloaded_at DESC, snapshot_id DESC
    LIMIT 1
),
counts AS (
    SELECT
        l.snapshot_id,
        l.source_row_count,
        l.downloaded_at,
        l.source_sha256,
        (
            SELECT COUNT(*)
            FROM raw.cms_hospital_records r
            WHERE r.snapshot_id = l.snapshot_id
        ) AS raw_rows,
        (
            SELECT COUNT(*)
            FROM core.hospitals h
            WHERE h.snapshot_id = l.snapshot_id
        ) AS core_rows
    FROM latest l
)
SELECT
    snapshot_id,
    source_row_count,
    raw_rows,
    core_rows,
    downloaded_at,
    source_sha256,
    (
        source_row_count = raw_rows
        AND raw_rows = core_rows
    ) AS reconciled
FROM counts;
