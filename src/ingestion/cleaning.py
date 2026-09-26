from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import normalize_whitespace, write_csv
from ingestion.crossref import PaperRecord


def _clean_text(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    return normalize_whitespace(cleaned)


def _join_list(items: Any, sep: str = ", ") -> str:
    if isinstance(items, list):
        return sep.join(normalize_whitespace(str(x)) for x in items if str(x).strip())
    return normalize_whitespace(str(items or ""))


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records thanh dataframe san sang de embed.

    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days = (run_date - published).days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding (cau truc 5 phan)
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    if not records:
        return pd.DataFrame()

    raw_dicts = [asdict(r) for r in records]
    df = pd.DataFrame(raw_dicts)

    # 1. Normalize text fields
    df["paper_id"] = df["paper_id"].astype(str).str.strip()
    df["title"] = df["title"].apply(_clean_text)
    df["summary"] = df["summary"].apply(_clean_text)
    df["primary_category"] = df["primary_category"].astype(str).str.strip()
    df["abs_url"] = df["abs_url"].astype(str).str.strip()
    df["pdf_url"] = df["pdf_url"].astype(str).str.strip()
    df["comment"] = df["comment"].astype(str).str.strip()

    # 2. Filter row xau va drop duplicates theo paper_id
    df = df[df["paper_id"] != ""]
    df = df[df["title"] != ""]
    df = df.drop_duplicates(subset=["paper_id"], keep="first")

    # 3. Parse published date va tinh age_days
    run_dt = run_date if run_date.tzinfo is not None else run_date.replace(tzinfo=timezone.utc)
    pub_dates = pd.to_datetime(df["published"], utc=True, errors="coerce")
    df["age_days"] = (run_dt - pub_dates).dt.days.fillna(0).astype(int)

    # 4. Helper columns
    df["authors_joined"] = df["authors"].apply(_join_list)
    df["categories_joined"] = df["categories"].apply(_join_list)
    df["summary_chars"] = df["summary"].str.len().fillna(0).astype(int)

    # Cột text_for_embedding có cấu trúc 5 phần chuẩn
    df["text_for_embedding"] = (
        "Title: " + df["title"] + "\n" +
        "Authors: " + df["authors_joined"] + "\n" +
        "Published: " + df["published"].astype(str) + "\n" +
        "Abstract: " + df["summary"] + "\n" +
        "Categories: " + df["categories_joined"]
    )

    # 5. Sort dataframe theo published giam dan va paper_id
    df = df.sort_values(by=["published", "paper_id"], ascending=[False, True]).reset_index(drop=True)
    return df


def save_clean_dataframe(df: pd.DataFrame, settings: Settings) -> None:
    """Luu clean dataframe ra ca CSV va JSON."""
    write_csv(df, settings.paths.clean_csv)
    settings.paths.clean_json.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(settings.paths.clean_json, orient="records", indent=2, force_ascii=False)

