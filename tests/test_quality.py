from __future__ import annotations

import pandas as pd
from src.core.config import load_settings
from src.observability.quality import build_freshness_report, run_data_quality_checks


def test_quality_checks_baseline_pass():
    settings = load_settings()
    clean_df = pd.read_json(settings.paths.clean_json)
    
    q_result = run_data_quality_checks(clean_df, settings, "pytest_test")
    assert q_result["success"] is True
    assert q_result["failed_expectations"] == 0

    f_result = build_freshness_report(clean_df, settings, settings.paths.quality_dir / "pytest_freshness.json")
    assert f_result["is_fresh"] is True
    assert f_result["stale_ratio"] <= 0.25
