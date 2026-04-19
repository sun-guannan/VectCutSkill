#!/usr/bin/env python3
"""Search VectCut API docs from the online llms.txt index."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import re
import sys
from typing import Iterable

import requests

ENTRY_URL = "https://docs.vectcut.com/llms.txt"
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


@dataclasses.dataclass
class DocItem:
    section: str
    label: str
    title: str
    url: str
    description: str


def fetch_text(url: str, timeout: float = 20.0) -> str:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def split_keywords(query: str) -> list[str]:
    query = normalize(query)
    if not query:
        return []
    return [p for p in re.split(r"[\s,，;；|/]+", query) if p]


def parse_llms_index(content: str) -> list[DocItem]:
    items: list[DocItem] = []
    current_section = ""

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        if not line.startswith("- "):
            continue

        matches = LINK_RE.findall(line)
        if not matches:
            continue

        first_bracket = line.find("[")
        prefix = line[2:first_bracket].strip() if first_bracket >= 0 else ""
        description = ""
        if "):" in line:
            description = line.split("):", 1)[1].strip()

        for title, url in matches:
            label = f"{prefix} {title}".strip()
            items.append(
                DocItem(
                    section=current_section,
                    label=label or title,
                    title=title.strip(),
                    url=url.strip(),
                    description=description,
                )
            )

    return items


def filter_by_scope(items: Iterable[DocItem], scope: str) -> list[DocItem]:
    if scope == "all":
        return list(items)
    return [item for item in items if normalize(item.section) == "api docs"]


def score_item(item: DocItem, keywords: list[str]) -> int:
    if not keywords:
        return 0
    title_norm = normalize(item.title)
    label_norm = normalize(item.label)
    haystack = " ".join(
        [
            normalize(item.section),
            label_norm,
            title_norm,
            normalize(item.description),
            normalize(item.url),
        ]
    )
    score = 0
    for kw in keywords:
        if kw == title_norm:
            score += 10
            continue
        if kw in title_norm:
            score += 6
            continue
        if kw in label_norm:
            score += 4
            continue
        if kw in haystack:
            score += 2
        elif any(part in haystack for part in kw.split("_")):
            score += 1
    return score


def fetch_details(url: str, timeout: float = 20.0) -> dict[str, str]:
    text = fetch_text(url, timeout=timeout)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    snippet = "\n".join(lines[:20])
    return {"snippet": snippet}


def search(
    query: str,
    scope: str,
    max_results: int,
    with_details: bool,
    timeout: float,
) -> dict:
    index_text = fetch_text(ENTRY_URL, timeout=timeout)
    all_items = parse_llms_index(index_text)
    scoped_items = filter_by_scope(all_items, scope=scope)
    keywords = split_keywords(query)

    ranked = sorted(
        scoped_items,
        key=lambda item: (score_item(item, keywords), item.label),
        reverse=True,
    )
    if keywords:
        ranked = [it for it in ranked if score_item(it, keywords) > 0]

    selected = ranked[:max_results]
    results = []
    for item in selected:
        row = dataclasses.asdict(item)
        if with_details:
            try:
                row.update(fetch_details(item.url, timeout=timeout))
            except Exception as exc:  # noqa: BLE001
                row["snippet_error"] = str(exc)
        results.append(row)

    return {
        "entry_url": ENTRY_URL,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "query": query,
        "scope": scope,
        "total_index_items": len(all_items),
        "total_scoped_items": len(scoped_items),
        "matched_count": len(results),
        "matches": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search VectCut API docs online")
    parser.add_argument("--query", default="", help="Search query, supports zh/en")
    parser.add_argument("--scope", choices=["api", "all"], default="api")
    parser.add_argument("--max-results", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--no-fetch-details", action="store_true")
    parser.add_argument("--output", default="", help="Optional output json file path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = search(
            query=args.query,
            scope=args.scope,
            max_results=max(1, args.max_results),
            with_details=not args.no_fetch_details,
            timeout=max(1.0, args.timeout),
        )
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    payload = {"success": True, **data}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
