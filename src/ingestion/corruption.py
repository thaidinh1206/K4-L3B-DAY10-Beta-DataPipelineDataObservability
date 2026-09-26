from __future__ import annotations

import random
import string
from pathlib import Path

import pandas as pd

from core.utils import write_json


def _rebuild_text_for_embedding(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild text_for_embedding column from current field values."""
    df = df.copy()
    df["text_for_embedding"] = df.apply(
        lambda row: (
            f"Title: {row.get('title', '')}\n"
            f"Authors: {row.get('authors_joined', '')}\n"
            f"Categories: {row.get('categories_joined', '')}\n"
            f"Published: {row.get('published', '')}\n"
            f"Summary: {row.get('summary', '')}"
        ).strip(),
        axis=1,
    )
    return df


def corrupt_clean_dataframe(clean_df: pd.DataFrame, log_path) -> pd.DataFrame:
    """Simulate 6 types of data corruption on the clean dataframe.

    Corruption types:
    1. drop_latest_records — remove ~20% newest rows
    2. blank_summary       — clear summary for ~15% of rows
    3. inject_noise        — inject random chars into summary for ~15% of rows
    4. truncate_title      — shorten title to <8 chars for ~10% of rows
    5. stale_date          — push published date back 400+ days for ~10% of rows
    6. duplicate_rows      — duplicate ~10% of rows

    Writes corruption log to log_path (data/results/corruption_log.json).
    Returns corrupted dataframe.
    """
    rng   = random.Random(42)
    log: list[dict] = []
    df    = clean_df.copy().reset_index(drop=True)
    total = len(df)

    # ── 1. Drop latest records (~20%) ────────────────────────────────
    n_drop     = max(1, int(total * 0.20))
    by_date    = df.sort_values("published", ascending=False)
    drop_idx   = list(by_date.index[:n_drop])
    dropped_ids = df.loc[drop_idx, "paper_id"].tolist()
    df = df.drop(index=drop_idx).reset_index(drop=True)
    log.append({
        "corruption_type": "drop_latest_records",
        "affected_count":  n_drop,
        "affected_ids":    dropped_ids,
        "description":     f"Dropped {n_drop} most-recent records ({n_drop/total*100:.0f}% of total).",
    })

    # ── 2. Blank summary (~15%) ──────────────────────────────────────
    n_blank    = max(1, int(len(df) * 0.15))
    blank_idx  = rng.sample(range(len(df)), n_blank)
    blank_ids  = df.loc[blank_idx, "paper_id"].tolist()
    df.loc[blank_idx, "summary"]       = ""
    df.loc[blank_idx, "summary_chars"] = 0
    log.append({
        "corruption_type": "blank_summary",
        "affected_count":  n_blank,
        "affected_ids":    blank_ids,
        "description":     f"Blanked summary for {n_blank} rows.",
    })

    # ── 3. Inject noise (~15%) ───────────────────────────────────────
    n_noise    = max(1, int(len(df) * 0.15))
    noise_idx  = rng.sample(range(len(df)), n_noise)
    noise_ids  = df.loc[noise_idx, "paper_id"].tolist()
    noise_chars = string.punctuation + "###$$$@@@"
    for idx in noise_idx:
        junk = "".join(rng.choices(noise_chars, k=30))
        df.loc[idx, "summary"] = junk + " " + str(df.loc[idx, "summary"])
    log.append({
        "corruption_type": "inject_noise",
        "affected_count":  n_noise,
        "affected_ids":    noise_ids,
        "description":     f"Injected random noise characters into summary for {n_noise} rows.",
    })

    # ── 4. Truncate title (~10%) ─────────────────────────────────────
    n_trunc   = max(1, int(len(df) * 0.10))
    trunc_idx = rng.sample(range(len(df)), n_trunc)
    trunc_ids = df.loc[trunc_idx, "paper_id"].tolist()
    for idx in trunc_idx:
        df.loc[idx, "title"] = str(df.loc[idx, "title"])[:7]   # < 8 chars
    log.append({
        "corruption_type": "truncate_title",
        "affected_count":  n_trunc,
        "affected_ids":    trunc_ids,
        "description":     f"Truncated title to <8 characters for {n_trunc} rows.",
    })

    # ── 5. Stale date (~10%) ─────────────────────────────────────────
    n_stale   = max(1, int(len(df) * 0.10))
    stale_idx = rng.sample(range(len(df)), n_stale)
    stale_ids = df.loc[stale_idx, "paper_id"].tolist()
    for idx in stale_idx:
        df.loc[idx, "published"] = "2020-01-01"
        df.loc[idx, "updated"]   = "2020-01-01"
        if "age_days" in df.columns:
            df.loc[idx, "age_days"] = 2400
    log.append({
        "corruption_type": "stale_date",
        "affected_count":  n_stale,
        "affected_ids":    stale_ids,
        "description":     f"Set published date to 2020-01-01 (>400 days ago) for {n_stale} rows.",
    })

    # ── 6. Duplicate rows (~10%) ─────────────────────────────────────
    n_dup   = max(1, int(len(df) * 0.10))
    dup_idx = rng.sample(range(len(df)), n_dup)
    dup_ids = df.loc[dup_idx, "paper_id"].tolist()
    df = pd.concat([df, df.loc[dup_idx].copy()], ignore_index=True)
    log.append({
        "corruption_type": "duplicate_rows",
        "affected_count":  n_dup,
        "affected_ids":    dup_ids,
        "description":     f"Duplicated {n_dup} rows.",
    })

    # ── Rebuild text_for_embedding ───────────────────────────────────
    df = _rebuild_text_for_embedding(df)

    # ── Write corruption log ─────────────────────────────────────────
    write_json(Path(log_path), log)

    total_after = len(df)
    print(f"[corruption] Applied 6 corruption types. Rows: {total} → {total_after}")
    for entry in log:
        print(f"  • {entry['corruption_type']}: {entry['description']}")

    return df
