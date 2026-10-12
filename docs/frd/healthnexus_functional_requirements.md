
# HealthNexus 360 — Functional Requirements Document

Version: 1.0

## FR-001: Database Connectivity

The application shall connect to PostgreSQL using environment-based
credentials without exposing secrets in source control.

## FR-002: Source Ingestion

The ingestion pipeline shall download official CMS hospital records,
validate required columns and preserve source snapshot metadata.

## FR-003: Data Quality

The pipeline shall reject invalid records and prevent partial
publication of a hospital snapshot.

## FR-004: Reconciliation

The platform shall compare source, raw and core record counts.

## FR-005: Hospital Dashboard

The dashboard shall display hospital count, rating coverage,
average reported rating and emergency service availability.

## FR-006: Filtering

Users shall filter hospitals by state or territory and hospital type.

## FR-007: Facility Explorer

Users shall search hospitals by name or CMS facility identifier.

## FR-008: Data Export

Users shall download the currently filtered hospital records as CSV.

## FR-009: Pipeline Monitoring

The platform shall display recent ingestion executions and
their status, record counts and error information.

## FR-010: KPI Governance

KPI definitions, formulas, denominator policies and limitations
shall be stored in a versioned machine-readable contract.

## Nonfunctional Requirements

- No hardcoded credentials
- No fabricated operational KPIs
- No Docker dependency
- Parameterized SQL queries
- Automated linting and unit tests
- Clear handling of missing values
- Responsive Streamlit interface
- Public-data-only executive reporting

## Acceptance Criteria

1. Latest CMS snapshot reconciles across warehouse layers.
2. Dashboard totals match the latest core hospital snapshot.
3. Filtering updates KPI values and visualizations.
4. Missing ratings remain separate from one-star ratings.
5. Database failures produce user-readable error messages.
6. Source lineage and execution history remain inspectable.
