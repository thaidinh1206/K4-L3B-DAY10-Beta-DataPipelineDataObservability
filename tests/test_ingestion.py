from __future__ import annotations

from pathlib import Path
from src.ingestion.crossref import PaperRecord, parse_crossref_payload, load_raw_records


def test_parse_crossref_payload_valid():
    sample_payload = {
        "status": "ok",
        "message": {
            "items": [
                {
                    "DOI": "10.1145/test.001",
                    "title": ["<jats:p>Sample Paper Title</jats:p>"],
                    "abstract": "<jats:p>This is a test abstract for RAG pipeline.</jats:p>",
                    "author": [{"given": "Test", "family": "Author"}],
                    "subject": ["Computer Science"],
                    "published": {"date-parts": [[2026, 5, 20]]},
                    "created": {"date-time": "2026-05-20T10:00:00Z"},
                    "URL": "https://doi.org/10.1145/test.001",
                }
            ]
        },
    }

    records = parse_crossref_payload(sample_payload)
    assert len(records) == 1
    rec = records[0]
    assert rec.paper_id == "10.1145/test.001"
    assert rec.title == "Sample Paper Title"
    assert rec.summary == "This is a test abstract for RAG pipeline."
    assert rec.authors == ["Test Author"]
    assert rec.categories == ["Computer Science"]
    assert rec.published == "2026-05-20"


def test_load_raw_records_from_file():
    raw_path = Path("data/raw/crossref_records.json")
    if raw_path.exists():
        records = load_raw_records(raw_path)
        assert len(records) > 0
        assert isinstance(records[0], PaperRecord)
