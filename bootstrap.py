
from pathlib import Path

DIRECTORIES = [
    "app",
    "app/pages",
    "app/components",
    "app/services",
    "app/styles",
    "app/assets",
    "config",
    "database/migrations",
    "database/schemas",
    "database/views",
    "database/marts",
    "pipelines/ingestion",
    "pipelines/cleaning",
    "pipelines/validation",
    "pipelines/transformation",
    "analytics/eda",
    "analytics/statistics",
    "analytics/benchmarking",
    "analytics/insights",
    "analytics/impact_simulator",
    "governance/metric_contracts",
    "governance/quality_rules",
    "ml/features",
    "ml/training",
    "ml/evaluation",
    "ml/inference",
    "ai",
    "crm",
    "actions",
    "monitoring",
    "powerbi/dax",
    "powerbi/model",
    "powerbi/reports",
    "reports/generators",
    "reports/outputs",
    "docs/brd",
    "docs/frd",
    "docs/architecture",
    "docs/data_dictionary",
    "docs/kpi_catalog",
    "docs/deployment",
    "docs/interview",
    "presentations",
    "tests",
    "scripts",
    ".github/workflows",
    ".streamlit",
]

PACKAGES = [
    "app",
    "app/components",
    "app/services",
    "config",
    "pipelines",
    "analytics",
    "governance",
    "ml",
    "ai",
    "crm",
    "actions",
    "monitoring",
    "reports",
    "reports/generators",
]

def main():
    root = Path(__file__).resolve().parent

    for directory in DIRECTORIES:
        (root / directory).mkdir(
            parents=True,
            exist_ok=True,
        )

    for package in PACKAGES:
        path = root / package / "__init__.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)

    print("HealthNexus 360 structure created successfully.")

if __name__ == "__main__":
    main()
