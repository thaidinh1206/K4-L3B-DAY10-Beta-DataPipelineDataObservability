from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any

import requests

from core.config import Settings
from core.utils import normalize_whitespace, read_json, write_json


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_jats_xml(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return normalize_whitespace(cleaned)


def parse_crossref_payload(payload: dict[str, Any]) -> list[PaperRecord]:
    """Parse Crossref payload thanh list PaperRecord."""
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        paper_id = str(item.get("DOI", "")).strip()
        if not paper_id:
            continue

        raw_titles = item.get("title", [])
        raw_title = raw_titles[0] if isinstance(raw_titles, list) and raw_titles else str(raw_titles or "")
        title = _clean_jats_xml(raw_title) or "Untitled"

        abstract = item.get("abstract", "")
        summary = _clean_jats_xml(str(abstract))

        authors_raw = item.get("author", [])
        authors: list[str] = []
        if isinstance(authors_raw, list):
            for a in authors_raw:
                given = str(a.get("given", "")).strip()
                family = str(a.get("family", "")).strip()
                full_name = f"{given} {family}".strip()
                if full_name:
                    authors.append(full_name)
        if not authors:
            authors = ["Unknown"]

        cats = item.get("subject", [])
        if isinstance(cats, list) and cats:
            categories = [normalize_whitespace(str(c)) for c in cats if str(c).strip()]
        else:
            categories = ["General"]
        if not categories:
            categories = ["General"]
        primary_category = categories[0]

        pub_date = ""
        date_parts = item.get("published", {}).get("date-parts", [])
        if date_parts and isinstance(date_parts, list) and len(date_parts) > 0:
            dp = date_parts[0]
            if len(dp) >= 3:
                pub_date = f"{int(dp[0]):04d}-{int(dp[1]):02d}-{int(dp[2]):02d}"
            elif len(dp) == 2:
                pub_date = f"{int(dp[0]):04d}-{int(dp[1]):02d}-01"
            elif len(dp) == 1:
                pub_date = f"{int(dp[0]):04d}-01-01"
        if not pub_date:
            created = item.get("created", {}).get("date-time", "")
            if created and len(created) >= 10:
                pub_date = created[:10]
            else:
                pub_date = "2026-01-01"

        created = item.get("created", {}).get("date-time", "")
        updated = created[:10] if (created and len(created) >= 10) else pub_date

        url = str(item.get("URL", f"https://doi.org/{paper_id}")).strip()

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=pub_date,
                updated=updated,
                abs_url=url,
                pdf_url=url,
                comment=f"Crossref record {paper_id}",
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Goi source API, luu raw response, parse thanh records (co fallback snapshot)."""
    payload: dict[str, Any] | None = None

    if settings.refresh_source:
        try:
            url = "https://api.crossref.org/works"
            params = {
                "query": settings.source_query,
                "filter": settings.source_filter,
                "rows": settings.max_results,
            }
            headers = {
                "User-Agent": "Day10DataObservabilityLab/1.0 (mailto:student@vinuni.edu.vn)"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                payload = response.json()
                write_json(settings.paths.raw_api_response, payload)
        except Exception:
            payload = None

    if payload is None:
        if settings.paths.raw_api_response.exists():
            payload = read_json(settings.paths.raw_api_response)
        else:
            raise FileNotFoundError(
                f"Snapshot not found at {settings.paths.raw_api_response} and API call failed."
            )

    records = parse_crossref_payload(payload)
    records_dict = [asdict(r) for r in records]
    write_json(settings.paths.raw_records_json, records_dict)
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Doc JSON snapshot va map thanh `PaperRecord`."""
    data = read_json(path)
    return [PaperRecord(**item) for item in data]
