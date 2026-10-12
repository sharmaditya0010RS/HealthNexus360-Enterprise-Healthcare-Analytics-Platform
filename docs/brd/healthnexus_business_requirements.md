
# HealthNexus 360 — Business Requirements Document

Version: 1.0  
Status: Portfolio demonstration specification

## Business Problem

Healthcare leaders need a transparent way to explore public hospital
performance data, identify reporting gaps, compare facilities and
prioritize further investigation.

## Primary Stakeholders

- Healthcare executive
- Hospital quality director
- Business intelligence analyst
- Data engineering team
- Compliance and data governance reviewer

## Business Objectives

1. Consolidate official CMS hospital records into a governed warehouse.
2. Measure hospital rating availability and descriptive rating patterns.
3. Compare geographic and facility-type segments.
4. Provide auditable data lineage and reconciliation.
5. Enable nontechnical users to explore and export hospital data.

## In Scope

- CMS Hospital General Information
- Hospital counts and reporting coverage
- Overall star rating distribution
- Emergency services availability
- State and hospital-type comparisons
- Ingestion monitoring and data-quality reporting

## Out of Scope for This Release

- Patient-level clinical analysis
- Actual readmission rate modeling
- Causal claims about hospital performance
- Observed financial savings
- Patient-identifiable information

## Business Success Criteria

- Source, raw and core row counts reconcile.
- Every published KPI has a documented definition.
- Users can filter hospital records by geography and type.
- Missing ratings are not treated as zero.
- Dashboard exports reflect the selected filters.
- Ingestion runs are recorded in the audit schema.

## Decision Use

The dashboard supports prioritizing hospitals or regions for further
investigation. It does not establish clinical superiority or causality.

## Data Limitations

CMS data is public and may change between releases. Overall ratings
have incomplete coverage and are not equivalent to patient-level
outcomes. State-level comparisons are descriptive and should be
interpreted alongside hospital mix and rating availability.
