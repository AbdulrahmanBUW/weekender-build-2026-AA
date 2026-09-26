#!/usr/bin/env python3
"""Export what is live in the app into review sheets, so the team can check and improve it in Google Sheets.

    python scripts/export_review.py            # family providers + upcoming events -> docs/content-kit/review/
    python scripts/export_review.py --all      # also newcomer services (doctors, banks, ...) and past events
    python scripts/export_review.py -d OUTDIR  # write somewhere else

The files have the same columns as the content-kit templates, plus:
    Review, Review note   what the reviewer fills in (empty / ok, fix, remove)
    Description (de) ...  one column per language instead of Translations (JSON)
    ID                    never edit; it tells scripts/import_content.py which entry to update
Re-import an edited sheet with scripts/import_content.py (dry run first, then --apply). See docs/content-kit/README.md.

Reads the linked (live) Supabase project via `npx -y supabase db query --linked`. Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LANGS = ["de", "ru", "uk", "ar", "tr"]

PROVIDERS_SQL = """
select id, category, subcategory, name, address, district, phone, website,
       array_to_string(languages, ';') as languages, array_to_string(activity_categories, ';') as activity_categories,
       age_min_years, age_max_years, price_type, format, opening_hours, description_en, i18n, source_url, notes_en
from public.resources
{where}
order by category, name
"""

EVENTS_SQL = """
select e.id, e.title,
       to_char(e.starts_at at time zone 'Europe/Berlin', 'YYYY-MM-DD HH24:MI') as starts_at,
       to_char(e.ends_at at time zone 'Europe/Berlin', 'YYYY-MM-DD HH24:MI') as ends_at,
       e.all_day, e.place_name, e.address, e.district, r.name as provider_name, e.age_min_years, e.age_max_years,
       array_to_string(e.languages, ';') as languages, array_to_string(e.activity_categories, ';') as activity_categories,
       e.price_type, e.price_text, e.url, e.description_en, e.i18n, e.source_url
from public.family_events e
left join public.resources r on r.id = e.resource_id
{where}
order by e.starts_at, e.title
"""

REVIEW_HEAD = ["Review", "Review note"]
PROVIDER_HEAD = ["Category", "Subcategory", "Name", "Address", "District", "Phone", "Website", "Languages",
                 "Activity categories", "Min age (years)", "Max age (years)", "Price type", "Format", "Opening hours",
                 "Description (English)"] + [f"Description ({l})" for l in LANGS] + ["Source link", "Notes", "ID"]
EVENT_HEAD = (["Title"] + [f"Title ({l})" for l in LANGS] +
              ["Starts at", "Ends at", "All day", "Place name", "Address", "District", "Provider name",
               "Min age (years)", "Max age (years)", "Languages", "Activity categories", "Price type", "Price text",
               "Event link", "Description (English)"] + [f"Description ({l})" for l in LANGS] + ["Source link", "ID"])


def query(sql: str) -> list:
    npx = shutil.which("npx")
    if not npx:
        sys.exit("STOP: 'npx' was not found. Install Node.js (https://nodejs.org).")
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        tmp = f.name
    try:
        res = subprocess.run([npx, "-y", "supabase", "db", "query", "--linked", "-f", tmp], cwd=REPO_ROOT,
                             capture_output=True, text=True, encoding="utf-8")
    finally:
        Path(tmp).unlink(missing_ok=True)
    out = res.stdout or ""
    if res.returncode != 0 or "{" not in out:
        sys.exit("STOP: the database query failed:\n" + (res.stderr or out)[-2000:])
    data = json.loads(out[out.index("{"): out.rindex("}") + 1])
    return data.get("rows", [])


def num(v) -> str:
    if v in (None, ""):
        return ""
    f = float(v)
    return str(int(f)) if f.is_integer() else f"{f:g}"


def tr(row: dict, lang: str, key: str) -> str:
    i18n = row.get("i18n") or {}
    if isinstance(i18n, str):
        i18n = json.loads(i18n or "{}")
    return ((i18n.get(lang) or {}).get(key) or "") if isinstance(i18n.get(lang), dict) else ""


def s(v) -> str:
    return "" if v is None else str(v)


def provider_line(r: dict) -> list:
    return (["", ""] + [s(r["category"]), s(r["subcategory"]), s(r["name"]), s(r["address"]), s(r["district"]),
                        s(r["phone"]), s(r["website"]), s(r["languages"]), s(r["activity_categories"]),
                        num(r["age_min_years"]), num(r["age_max_years"]), s(r["price_type"]), s(r["format"]),
                        s(r["opening_hours"]), s(r["description_en"])]
            + [tr(r, l, "description") for l in LANGS] + [s(r["source_url"]), s(r["notes_en"]), s(r["id"])])


def event_line(r: dict) -> list:
    return (["", "", s(r["title"])] + [tr(r, l, "title") for l in LANGS] +
            [s(r["starts_at"]), s(r["ends_at"]), "yes" if r.get("all_day") in (True, "true", "t") else "no",
             s(r["place_name"]), s(r["address"]), s(r["district"]), s(r["provider_name"]),
             num(r["age_min_years"]), num(r["age_max_years"]), s(r["languages"]), s(r["activity_categories"]),
             s(r["price_type"]), s(r["price_text"]), s(r["url"]), s(r["description_en"])]
            + [tr(r, l, "description") for l in LANGS] + [s(r["source_url"]), s(r["id"])])


def write(path: Path, head: list, lines: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:   # BOM: Excel shows umlauts and Cyrillic correctly
        w = csv.writer(f)
        w.writerow(REVIEW_HEAD + head)
        w.writerows(lines)
    print(f"{len(lines):>4} rows -> {path}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Export live providers and events into review sheets (CSV).")
    ap.add_argument("--all", action="store_true", help="include newcomer services and past events")
    ap.add_argument("-d", "--dir", default=str(REPO_ROOT / "docs" / "content-kit" / "review"), help="output folder")
    a = ap.parse_args()

    out = Path(a.dir)
    p_where = "" if a.all else "where audience in ('family', 'both')"
    e_where = "" if a.all else "where coalesce(e.ends_at, e.starts_at) >= now() - interval '12 hours'"
    providers = query(PROVIDERS_SQL.format(where=p_where))
    events = query(EVENTS_SQL.format(where=e_where))
    write(out / "providers-review.csv", PROVIDER_HEAD, [provider_line(r) for r in providers])
    write(out / "events-review.csv", EVENT_HEAD, [event_line(r) for r in events])
    print("Next: import both files into a Google Sheet, review, then follow docs/content-kit/README.md "
          "(section 'Review and improve what is already in the app').")
    return 0


if __name__ == "__main__":
    sys.exit(main())
