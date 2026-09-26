from __future__ import annotations

from datetime import datetime, timezone

from src.ingestion.cleaning import build_clean_dataframe
from src.ingestion.crossref import PaperRecord


def test_build_clean_dataframe_deduplication_and_text_embedding():
    rec1 = PaperRecord(
        paper_id="10.1145/001",
        title="  Paper One Title  ",
        summary="Summary for paper one abstract.",
        authors=["Alice", "Bob"],
        categories=["AI"],
        primary_category="AI",
        published="2026-05-01",
        updated="2026-05-01",
        abs_url="https://doi.org/10.1145/001",
        pdf_url="https://doi.org/10.1145/001",
        comment="Test",
    )
    # Duplicate paper_id
    rec2 = PaperRecord(
        paper_id="10.1145/001",
        title="Paper One Title Duplicate",
        summary="Duplicate summary.",
        authors=["Alice"],
        categories=["AI"],
        primary_category="AI",
        published="2026-05-01",
        updated="2026-05-01",
        abs_url="https://doi.org/10.1145/001",
        pdf_url="https://doi.org/10.1145/001",
        comment="Duplicate Test",
    )

    records = [rec1, rec2]
    now = datetime(2026, 6, 1, tzinfo=timezone.utc)
    df = build_clean_dataframe(records, now)

    # Must deduplicate
    assert len(df) == 1
    row = df.iloc[0]
    assert row["paper_id"] == "10.1145/001"
    assert row["title"] == "Paper One Title"
    assert row["age_days"] == 31  # May 1 to June 1 is 31 days
    assert "Title: Paper One Title" in row["text_for_embedding"]
    assert "Authors: Alice, Bob" in row["text_for_embedding"]
    assert "Abstract: Summary for paper one abstract." in row["text_for_embedding"]
