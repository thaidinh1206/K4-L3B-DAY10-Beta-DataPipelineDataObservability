from __future__ import annotations

import pandas as pd
from src.core.config import load_settings
from src.ingestion.corruption import corrupt_clean_dataframe
from src.observability.quality import run_data_quality_checks


def test_corruption_triggers_quality_failure():
    settings = load_settings()
    clean_df = pd.read_json(settings.paths.clean_json)

    log_path = settings.paths.quality_dir / "pytest_corruption_log.json"
    corrupted_df = corrupt_clean_dataframe(clean_df, log_path)

    assert len(corrupted_df) > 0
    assert log_path.exists()

    # Data Quality Gate MUST fail on corrupted data
    q_result = run_data_quality_checks(corrupted_df, settings, "pytest_corrupted")
    assert q_result["success"] is False
    assert q_result["failed_expectations"] > 0
