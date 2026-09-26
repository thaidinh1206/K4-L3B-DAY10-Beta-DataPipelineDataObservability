from __future__ import annotations

from pathlib import Path
from typing import Any

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Tao bo data quality checks theo chuan Great Expectations 1.x.

    1. Khoi tao ephemeral context cua GX 1.x.
    2. Dinh nghia cac Expectations thiet yeu:
       - ExpectTableRowCountToBeBetween: 10 <= rows <= 100
       - ExpectColumnValuesToNotBeNull: paper_id, title, text_for_embedding
       - ExpectColumnValuesToBeUnique: paper_id
       - ExpectColumnValueLengthsToBeBetween: title (8-500), summary (20-5000)
    3. Validate va ghi report vao data/quality/{report_name}_quality_report.json.
    """
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas(name=f"papers_source_{report_name}")
    data_asset = data_source.add_dataframe_asset(name=f"papers_asset_{report_name}")
    batch_def = data_asset.add_batch_definition_whole_dataframe(f"papers_batch_{report_name}")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    suite = gx.ExpectationSuite(name=f"papers_suite_{report_name}")
    suite.add_expectation(gxe.ExpectTableRowCountToBeBetween(min_value=10, max_value=100))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="paper_id"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="title"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="text_for_embedding"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="paper_id"))
    suite.add_expectation(gxe.ExpectColumnValueLengthsToBeBetween(column="title", min_value=8, max_value=500))
    suite.add_expectation(gxe.ExpectColumnValueLengthsToBeBetween(column="summary", min_value=20, max_value=5000))
    context.suites.add(suite)

    validation_result = batch.validate(suite)
    success = bool(validation_result.success)

    report_dict: dict[str, Any] = {
        "report_name": report_name,
        "success": success,
        "total_records": len(df),
        "evaluated_expectations": len(validation_result.results),
        "successful_expectations": sum(1 for r in validation_result.results if r.success),
        "failed_expectations": sum(1 for r in validation_result.results if not r.success),
        "details": validation_result.to_json_dict(),
    }

    report_path = settings.paths.quality_dir / f"{report_name}_quality_report.json"
    write_json(report_path, report_dict)
    return report_dict


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path: Path | None = None) -> dict[str, Any]:
    """Tong hop freshness report va kiem tra Freshness SLA."""
    target_path = Path(report_path) if report_path is not None else settings.paths.freshness_report

    total_rows = len(df)
    latest_published = str(df["published"].max()) if not df.empty and "published" in df.columns else ""
    oldest_published = str(df["published"].min()) if not df.empty and "published" in df.columns else ""

    threshold = settings.freshness_threshold_days
    if not df.empty and "age_days" in df.columns:
        stale_rows = int((df["age_days"] > threshold).sum())
    else:
        stale_rows = 0

    stale_ratio = round(stale_rows / total_rows, 4) if total_rows > 0 else 0.0
    # Freshness SLA: canh bao is_fresh = False neu ty le bai bao co age_days > 180 vuot qua 25% (0.25)
    is_fresh = bool(stale_ratio <= 0.25)

    payload: dict[str, Any] = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "stale_ratio": stale_ratio,
        "freshness_threshold_days": threshold,
        "is_fresh": is_fresh,
    }

    write_json(target_path, payload)
    return payload

