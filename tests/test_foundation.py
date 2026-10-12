
from pathlib import Path

from app.pages.control_center import (
    available_reports,
)
from config.settings import Settings

ROOT = Path(__file__).resolve().parents[1]


def test_project_structure():
    required = [
        "app/main.py",
        "app/pages/home.py",
        "app/pages/control_center.py",
        "app/styles/main.css",
        "config/settings.py",
        "requirements.txt",
    ]

    for filename in required:
        assert (ROOT / filename).is_file()


def test_default_settings():
    settings = Settings(
        app_name="HealthNexus 360",
        app_env="development",
    )

    assert settings.app_name == "HealthNexus 360"
    assert settings.app_env == "development"


def test_report_types():
    for report_type in [
        "PDF",
        "Excel",
        "PowerPoint",
    ]:
        files = available_reports(report_type)
        assert isinstance(files, list)


def test_css_exists():
    css = (
        ROOT / "app" / "styles" / "main.css"
    ).read_text(encoding="utf-8")

    assert ".stApp" in css
    assert ".block-container" in css
