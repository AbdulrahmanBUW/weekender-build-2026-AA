#!/usr/bin/env python3
"""Import Dresden family providers or events from a spreadsheet (CSV) into Supabase.

    python scripts/import_content.py my-providers.csv            # check rows + write SQL (dry run)
    python scripts/import_content.py my-events.csv --apply       # check + write SQL + send to the live DB

Options:
    --type providers|events   force the file type (normally detected from the header row)
    -o / --out FILE.sql       where to write the SQL (default: next to the CSV, <name>.import.sql)
    --apply                   run the SQL on the linked (live) Supabase project via
                              `npx -y supabase db query --linked -f <sql>` from the repo root
    --skip-errors             with --apply: send the good rows even if other rows have errors
    --yes                     with --apply: do not ask for confirmation
    --include-examples        also turn EXAMPLE rows into SQL (for testing only; never with --apply)

Python 3 standard library only. The rules below mirror
supabase/migrations/20260926200000_merged_family_hub.sql - keep them in sync when the schema changes.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- allowed values (from the migration)
RESOURCE_CATEGORIES = [
    "course", "kita", "school", "library", "playground", "family_place", "community",  # family hub
    "auslaenderbehoerde", "doctor", "pharmacy", "bank", "other",                         # newcomer services
]
ACTIVITY_CATEGORIES = [
    "music", "dance", "sport", "yoga", "art", "languages", "stem", "swimming", "theatre", "nature",
    "parent_baby", "parent_meetup", "library", "school_kita", "family_cafe", "playground",
]
RESOURCE_PRICE_TYPES = ["free", "per_session", "subscription", "trial_available", "unknown"]
EVENT_PRICE_TYPES = ["free", "paid", "unknown"]
FORMATS = ["recurring_course", "workshop", "one_off", "community_group", "place", "service"]
AGE_MIN, AGE_MAX = 0, 18
DESCRIPTION_MAX = 600
TITLE_MAX = 160

# Friendly spellings people type in a sheet -> the value the database expects.
SYNONYMS = {
    "category": {"kurs": "course", "courses": "course", "kurse": "course", "kitas": "kita",
                 "kindergarten": "kita", "krippe": "kita", "schule": "school", "schools": "school",
                 "bibliothek": "library", "buecherei": "library", "bücherei": "library",
                 "spielplatz": "playground", "playgrounds": "playground", "familienzentrum": "family_place",
                 "family_centre": "family_place", "family_center": "family_place", "gemeinschaft": "community",
                 "communities": "community", "verein": "community"},
    "activity": {"musik": "music", "tanz": "dance", "tanzen": "dance", "sports": "sport",
                 "kunst": "art", "arts": "art", "language": "languages", "sprachen": "languages",
                 "science": "stem", "mint": "stem", "schwimmen": "swimming", "theater": "theatre",
                 "natur": "nature", "outdoor": "nature", "parent_and_baby": "parent_baby",
                 "eltern_kind": "parent_baby", "parents_meetup": "parent_meetup", "elterntreff": "parent_meetup",
                 "family_café": "family_cafe", "cafe": "family_cafe", "café": "family_cafe",
                 "spielplatz": "playground", "school": "school_kita", "kita": "school_kita"},
    "price_resource": {"kostenlos": "free", "gratis": "free", "0": "free", "session": "per_session",
                       "pay_per_session": "per_session", "abo": "subscription", "monthly": "subscription",
                       "trial": "trial_available", "free_trial": "trial_available",
                       "probestunde": "trial_available", "": "unknown"},
    "price_event": {"kostenlos": "free", "gratis": "free", "0": "free", "kostenpflichtig": "paid",
                    "ticket": "paid", "": "unknown"},
    "format": {"course": "recurring_course", "kurs": "recurring_course", "weekly": "recurring_course",
               "oneoff": "one_off", "one_time": "one_off", "event": "one_off", "group": "community_group",
               "community": "community_group", "ort": "place", "venue": "place", "beratung": "service"},
}

# ISO 639-1 codes + a few ISO 639-3 codes relevant in Dresden.
ISO_639_1 = set("""aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv
cy da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht hu hy hz ia id ie
ig ii ik io is it iu ja jv ka kg ki kj kk kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk
ml mn mr ms mt my na nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se
sg si sk sl sm sn so sq sr ss st su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo
xh yi yo za zh zu""".split())
ISO_EXTRA = {"prs": "Dari", "ckb": "Kurdish (Sorani)", "kmr": "Kurdish (Kurmanji)", "gsg": "German Sign Language",
             "hsb": "Upper Sorbian", "yue": "Cantonese", "fil": "Filipino"}
LANG_CODES = ISO_639_1 | set(ISO_EXTRA)
LANG_NAMES = {
    "german": "de", "deutsch": "de", "english": "en", "englisch": "en", "arabic": "ar", "arabisch": "ar",
    "turkish": "tr", "türkisch": "tr", "tuerkisch": "tr", "ukrainian": "uk", "ukrainisch": "uk",
    "russian": "ru", "russisch": "ru", "persian": "fa", "farsi": "fa", "persisch": "fa", "dari": "prs",
    "hindi": "hi", "spanish": "es", "spanisch": "es", "french": "fr", "französisch": "fr", "franzoesisch": "fr",
    "polish": "pl", "polnisch": "pl", "vietnamese": "vi", "vietnamesisch": "vi", "chinese": "zh",
    "chinesisch": "zh", "mandarin": "zh", "italian": "it", "italienisch": "it", "portuguese": "pt",
    "portugiesisch": "pt", "kurdish": "ku", "kurdisch": "ku", "czech": "cs", "tschechisch": "cs",
    "romanian": "ro", "rumänisch": "ro", "bulgarian": "bg", "bulgarisch": "bg", "greek": "el",
    "griechisch": "el", "japanese": "ja", "japanisch": "ja", "korean": "ko", "koreanisch": "ko", "urdu": "ur",
    "pashto": "ps", "paschtu": "ps", "tigrinya": "ti", "somali": "so", "sign language": "gsg",
    "gebärdensprache": "gsg", "dgs": "gsg", "sorbian": "hsb", "sorbisch": "hsb",
}

# ---------------------------------------------------------------- columns (sheet header -> DB column)
PROVIDER_COLUMNS = [
    ("category", "Category"),
    ("subcategory", "Subcategory"),
    ("name", "Name"),
    ("address", "Address"),
    ("district", "District"),
    ("phone", "Phone"),
    ("website", "Website"),
    ("languages", "Languages"),
    ("activity_categories", "Activity categories"),
    ("age_min_years", "Min age (years)"),
    ("age_max_years", "Max age (years)"),
    ("price_type", "Price type"),
    ("format", "Format"),
    ("opening_hours", "Opening hours"),
    ("description_en", "Description (English)"),
    ("i18n", "Translations (JSON)"),
    ("source_url", "Source link"),
    ("notes_en", "Notes"),
]
EVENT_COLUMNS = [
    ("title", "Title"),
    ("starts_at", "Starts at"),
    ("ends_at", "Ends at"),
    ("all_day", "All day"),
    ("place_name", "Place name"),
    ("address", "Address"),
    ("district", "District"),
    ("provider_name", "Provider name"),          # -> resource_id (looked up by name)
    ("age_min_years", "Min age (years)"),
    ("age_max_years", "Max age (years)"),
    ("languages", "Languages"),
    ("activity_categories", "Activity categories"),
    ("price_type", "Price type"),
    ("price_text", "Price text"),
    ("url", "Event link"),
    ("description_en", "Description (English)"),
    ("i18n", "Translations (JSON)"),
    ("source_url", "Source link"),
]
REQUIRED_HEADERS = {"providers": ["category", "name", "source_url"], "events": ["title", "starts_at", "source_url"]}
EXTRA_ALIASES = {"sub category": "subcategory", "source": "source_url", "source url": "source_url",
                 "link": "source_url", "description": "description_en", "translations": "i18n",
                 "resource": "provider_name", "provider": "provider_name", "start": "starts_at",
                 "end": "ends_at", "event url": "url", "notes": "notes_en", "min age": "age_min_years",
                 "max age": "age_max_years"}


def norm_header(h: str) -> str:
    h = re.sub(r"\(.*?\)", " ", h or "")            # "Min age (years)" -> "min age"
    return re.sub(r"[^0-9a-zäöüß]+", " ", h.lower()).strip()


def header_map(kind: str) -> dict:
    m = {}
    for field, label in (PROVIDER_COLUMNS if kind == "providers" else EVENT_COLUMNS):
        m[norm_header(label)] = field
        m[norm_header(field.replace("_", " "))] = field   # raw DB column names work too
    for alias, field in EXTRA_ALIASES.items():
        if field in dict(PROVIDER_COLUMNS if kind == "providers" else EVENT_COLUMNS):
            m.setdefault(alias, field)
    return m


# ---------------------------------------------------------------- small helpers
def clean(s) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\x00", "")).strip()


def split_list(raw: str) -> list:
    out = []
    for p in re.split(r"[;,|\n]+", raw or ""):
        p = p.strip()
        if p and p not in out:
            out.append(p)
    return out


def enum_key(raw: str) -> str:
    return re.sub(r"[\s\-/]+", "_", raw.strip().lower())


def q(s) -> str:
    """SQL string literal (standard_conforming_strings = on)."""
    if s is None:
        return "null"
    return "'" + str(s).replace("\x00", "").replace("'", "''") + "'"


def q_arr(items) -> str:
    return "array[" + ",".join(q(i) for i in items) + "]::text[]" if items else "'{}'::text[]"


def q_num(v) -> str:
    return "null" if v is None else f"{v:g}"


def q_ts(dt) -> str:
    """Local Dresden wall-clock time -> timestamptz, conversion done by Postgres."""
    return "null" if dt is None else f"(timestamp '{dt:%Y-%m-%d %H:%M:%S}' at time zone 'Europe/Berlin')"


URL_RE = re.compile(r"^https?://[^\s/$.?#][^\s]*$", re.I)
DOMAIN_RE = re.compile(r"^(www\.)?[a-z0-9\-]+(\.[a-z0-9\-]+)+(/\S*)?$", re.I)


class Row:
    def __init__(self, number: int, raw: dict):
        self.number, self.raw = number, raw
        self.values: dict = {}
        self.provided: set = set()        # columns she actually filled in (only these overwrite on update)
        self.errors: list = []
        self.warnings: list = []
        self.example = False
        self.label = ""

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


# ---------------------------------------------------------------- field validators
def v_enum(row, field, label, allowed, syn_key, required=False, default=None):
    raw = clean(row.raw.get(field))
    if not raw:
        if required:
            row.err(f"{label} is empty. Use one of: {', '.join(allowed)}")
        row.values[field] = default
        return
    key = enum_key(raw)
    val = SYNONYMS.get(syn_key, {}).get(key, key)
    if val not in allowed:
        row.err(f'{label} "{raw}" is not allowed. Use one of: {", ".join(allowed)}')
        return
    if val != key:
        row.warn(f'{label} "{raw}" was read as "{val}"')
    row.values[field] = val
    row.provided.add(field)


def v_text(row, field, label, required=False, max_len=None):
    raw = (row.raw.get(field) or "").replace("\x00", "").strip()
    if field in ("name", "address", "title", "place_name", "district"):
        raw = clean(raw)
    if not raw:
        if required:
            row.err(f"{label} is empty (required)")
        row.values[field] = None
        return
    if max_len and len(raw) > max_len:
        row.err(f"{label} is {len(raw)} characters long; the limit is {max_len}. Please shorten it.")
        return
    row.values[field] = raw
    row.provided.add(field)


def v_url(row, field, label):
    raw = clean(row.raw.get(field))
    if not raw:
        row.values[field] = None
        return
    if " " in raw:
        row.err(f'{label} "{raw}" contains spaces - is it really a web address?')
        return
    if not re.match(r"^https?://", raw, re.I):
        if DOMAIN_RE.match(raw):
            row.warn(f'{label} "{raw}" had no https:// - added it')
            raw = "https://" + raw
        else:
            row.err(f'{label} "{raw}" is not a web address (should start with https://)')
            return
    if not URL_RE.match(raw):
        row.err(f'{label} "{raw}" does not look like a valid web address')
        return
    row.values[field] = raw
    row.provided.add(field)


def v_languages(row, field="languages", label="Languages"):
    codes, converted = [], []
    for part in split_list(row.raw.get(field)):
        k = part.lower().strip()
        if k in LANG_CODES:
            code = k
        elif k in LANG_NAMES:
            code = LANG_NAMES[k]
            converted.append(f"{part} -> {code}")
        else:
            row.err(f'{label}: "{part}" is not a language code. Use 2-letter ISO codes like de, en, ar, uk, ru, tr, fa'
                    f' (Dari = prs, German Sign Language = gsg)')
            continue
        if code not in codes:
            codes.append(code)
    if converted:
        row.warn(f"{label} converted to codes: " + ", ".join(converted))
    row.values[field] = codes
    if codes:
        row.provided.add(field)


def v_activities(row, field="activity_categories", label="Activity categories"):
    vals = []
    for part in split_list(row.raw.get(field)):
        key = enum_key(part)
        val = SYNONYMS["activity"].get(key, key)
        if val not in ACTIVITY_CATEGORIES:
            row.err(f'{label}: "{part}" is not allowed. Use: {", ".join(ACTIVITY_CATEGORIES)}')
            continue
        if val != key:
            row.warn(f'{label}: "{part}" was read as "{val}"')
        if val not in vals:
            vals.append(val)
    row.values[field] = vals
    if vals:
        row.provided.add(field)


def v_age(row, field, label):
    raw = clean(row.raw.get(field))
    if not raw:
        row.values[field] = None
        return
    try:
        v = float(raw.replace(",", "."))
    except ValueError:
        row.err(f'{label} "{raw}" is not a number. Write years as a number, e.g. 3 or 0.5 (= 6 months)')
        return
    if not AGE_MIN <= v <= AGE_MAX:
        row.err(f"{label} {raw} is outside {AGE_MIN}-{AGE_MAX} years")
        return
    if round(v, 1) != v:
        row.warn(f"{label} {raw} rounded to {round(v, 1):g}")
    row.values[field] = round(v, 1)
    row.provided.add(field)


def v_ages(row):
    v_age(row, "age_min_years", "Min age")
    v_age(row, "age_max_years", "Max age")
    lo, hi = row.values.get("age_min_years"), row.values.get("age_max_years")
    if lo is not None and hi is not None and lo > hi:
        row.err(f"Min age ({lo:g}) is higher than Max age ({hi:g})")


def v_i18n(row, field="i18n", label="Translations (JSON)"):
    raw = (row.raw.get(field) or "").strip()
    row.values[field] = {}
    if not raw:
        return
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        row.err(f"{label} is not valid JSON ({e.msg}). Leave it empty if unsure.")
        return
    if not isinstance(obj, dict):
        row.err(f'{label} must be an object like {{"de": {{"description": "..."}}}}')
        return
    bad = [k for k in obj if k not in LANG_CODES]
    if bad:
        row.warn(f"{label}: keys should be language codes; unknown: {', '.join(bad)}")
    row.values[field] = obj
    row.provided.add(field)


def v_phone(row):
    raw = clean(row.raw.get("phone"))
    row.values["phone"] = raw or None
    if raw:
        row.provided.add("phone")
        if not re.fullmatch(r"[0-9+()/.\-\s]{5,30}", raw):
            row.warn(f'Phone "{raw}" looks unusual - please double-check')


DT_FORMATS = [("%Y-%m-%d %H:%M", True), ("%Y-%m-%dT%H:%M", True), ("%Y-%m-%d %H:%M:%S", True),
              ("%Y-%m-%dT%H:%M:%S", True), ("%d.%m.%Y %H:%M", True), ("%d.%m.%Y, %H:%M", True),
              ("%d.%m.%Y %H:%M:%S", True), ("%d/%m/%Y %H:%M", True), ("%Y-%m-%d", False),
              ("%d.%m.%Y", False), ("%d/%m/%Y", False)]


def parse_dt(raw: str):
    s = re.sub(r"\s*uhr\s*$", "", raw.strip(), flags=re.I)
    s = re.sub(r"(\d{4}\s+\d{1,2})\.(\d{2})$", r"\1:\2", s)       # "17.10.2026 10.00" -> "... 10:00"
    for fmt, has_time in DT_FORMATS:
        try:
            return datetime.strptime(s, fmt), has_time
        except ValueError:
            pass
    return None, False


def v_bool(raw: str):
    k = raw.strip().lower()
    if k in ("yes", "y", "true", "1", "ja", "x"):
        return True
    if k in ("no", "n", "false", "0", "nein"):
        return False
    return None


# ---------------------------------------------------------------- row checks
def check_provider(row: Row):
    v_enum(row, "category", "Category", RESOURCE_CATEGORIES, "category", required=True)
    v_text(row, "subcategory", "Subcategory")
    v_text(row, "name", "Name", required=True)
    v_text(row, "address", "Address")
    v_text(row, "district", "District")
    v_phone(row)
    v_url(row, "website", "Website")
    v_languages(row)
    v_activities(row)
    v_ages(row)
    v_enum(row, "price_type", "Price type", RESOURCE_PRICE_TYPES, "price_resource", default="unknown")
    v_enum(row, "format", "Format", FORMATS, "format")
    v_text(row, "opening_hours", "Opening hours")
    v_text(row, "description_en", "Description (English)", max_len=DESCRIPTION_MAX)
    v_i18n(row)
    v_url(row, "source_url", "Source link")
    v_text(row, "notes_en", "Notes")
    if not row.values.get("source_url"):
        if row.values.get("website"):
            row.values["source_url"] = row.values["website"]
            row.warn("Source link is empty - using the Website as source link")
        elif not any("Source link" in e for e in row.errors):
            row.err("Source link is empty. Every entry needs a link where the information can be checked.")
    if row.values.get("subcategory"):
        row.values["subcategory"] = enum_key(row.values["subcategory"])
    if not (row.raw.get("description_en") or "").strip():
        row.warn("No description - families will only see the name")
    if not row.values.get("languages"):
        row.warn("No languages - the language filter will not find this entry")
    row.label = row.values.get("name") or clean(row.raw.get("name")) or "(no name)"


def check_event(row: Row):
    v_text(row, "title", "Title", required=True, max_len=TITLE_MAX)
    start_raw, end_raw = clean(row.raw.get("starts_at")), clean(row.raw.get("ends_at"))
    start, start_has_time = parse_dt(start_raw) if start_raw else (None, False)
    if not start_raw:
        row.err("Starts at is empty (required). Write e.g. 2026-10-17 10:00 or 17.10.2026 10:00")
    elif start is None:
        row.err(f'Starts at "{start_raw}" is not a date. Write e.g. 2026-10-17 10:00 or 17.10.2026 10:00')
    end, end_has_time = parse_dt(end_raw) if end_raw else (None, False)
    if end_raw and end is None:
        row.err(f'Ends at "{end_raw}" is not a date. Write e.g. 2026-10-17 12:00')
    if end is not None and not end_has_time:
        end = end.replace(hour=23, minute=59)
    all_day_raw = clean(row.raw.get("all_day"))
    all_day = v_bool(all_day_raw) if all_day_raw else None
    if all_day_raw and all_day is None:
        row.err(f'All day "{all_day_raw}" - write yes or no')
    if all_day is None:
        all_day = bool(start is not None and not start_has_time)
    if start is not None and end is not None and end < start:
        row.err("Ends at is before Starts at")
    if start is not None and start.date() < date.today():
        row.warn(f"This event started in the past ({start:%d.%m.%Y})")
    row.values.update(starts_at=start, ends_at=end, all_day=all_day)
    if end is not None:
        row.provided.add("ends_at")
    v_text(row, "place_name", "Place name")
    v_text(row, "address", "Address")
    v_text(row, "district", "District")
    v_text(row, "provider_name", "Provider name")
    v_ages(row)
    v_languages(row)
    v_activities(row)
    v_enum(row, "price_type", "Price type", EVENT_PRICE_TYPES, "price_event", default="unknown")
    v_text(row, "price_text", "Price text")
    v_url(row, "url", "Event link")
    v_text(row, "description_en", "Description (English)", max_len=DESCRIPTION_MAX)
    v_i18n(row)
    v_url(row, "source_url", "Source link")
    if not row.values.get("source_url"):
        if row.values.get("url"):
            row.values["source_url"] = row.values["url"]
            row.warn("Source link is empty - using the Event link as source link")
        elif not any("Source link" in e for e in row.errors):
            row.err("Source link is empty. Every event needs a link where it can be checked.")
    if not row.values.get("languages"):
        row.warn("No languages - saved as German (de)")
    row.label = row.values.get("title") or clean(row.raw.get("title")) or "(no title)"


# ---------------------------------------------------------------- SQL
def verify_notice() -> str:
    return (f"Added by the Dresden mit Kind team from our own network on {date.today():%Y-%m-%d}. "
            "Times, prices, age groups and languages can change: please check with the provider before you go.")


def sql_provider(r: Row) -> str:
    v, p = r.values, r.provided
    notes = v.get("notes_en") or verify_notice()
    cols = {
        "category": q(v["category"]), "subcategory": q(v.get("subcategory")), "name": q(v["name"]),
        "address": q(v.get("address")), "district": q(v.get("district")), "phone": q(v.get("phone")),
        "website": q(v.get("website")), "languages": q_arr(v.get("languages")),
        "activity_categories": q_arr(v.get("activity_categories")),
        "age_min_years": q_num(v.get("age_min_years")), "age_max_years": q_num(v.get("age_max_years")),
        "price_type": q(v.get("price_type") or "unknown"), "format": q(v.get("format")),
        "opening_hours": q(v.get("opening_hours")), "description_en": q(v.get("description_en")),
        "i18n": q(json.dumps(v.get("i18n") or {}, ensure_ascii=False)) + "::jsonb",
        "audience": q("family"), "notes_en": q(notes), "source": q("manual"),
        "source_url": q(v["source_url"]), "retrieved_at": "now()",
    }
    # On update only overwrite what she filled in - an empty cell never erases existing data.
    updatable = ["subcategory", "district", "phone", "website", "languages", "activity_categories",
                 "age_min_years", "age_max_years", "price_type", "format", "opening_hours",
                 "description_en", "i18n", "notes_en"]
    sets = [f"{c} = excluded.{c}" for c in updatable if c in p]
    if "notes_en" not in p:
        sets.append("notes_en = coalesce(r.notes_en, excluded.notes_en)")
    sets += ["audience = case when r.audience = 'newcomer' then 'both' else r.audience end",
             "source = 'manual'", "source_url = excluded.source_url", "retrieved_at = now()"]
    return (f"-- sheet row {r.number}: {sql_comment(r.label)}\n"
            f"insert into public.resources as r ({', '.join(cols)})\n"
            f"values ({', '.join(cols.values())})\n"
            f"on conflict (dedupe_key) do update set\n  " + ",\n  ".join(sets) + "\n"
            f"returning {r.number} as sheet_row, (xmax = 0) as added, r.name as name, r.id")


def sql_event(r: Row) -> str:
    v, p = r.values, r.provided
    provider = v.get("provider_name")
    resource_sql = ("null" if not provider else
                    f"(select id from public.resources where lower(name) = lower({q(provider)}) "
                    f"order by (audience <> 'newcomer') desc, retrieved_at desc limit 1)")
    cols = {
        "title": q(v["title"]), "description_en": q(v.get("description_en")),
        "i18n": q(json.dumps(v.get("i18n") or {}, ensure_ascii=False)) + "::jsonb",
        "starts_at": q_ts(v["starts_at"]), "ends_at": q_ts(v.get("ends_at")),
        "all_day": "true" if v.get("all_day") else "false", "place_name": q(v.get("place_name")),
        "address": q(v.get("address")), "district": q(v.get("district")), "resource_id": resource_sql,
        "age_min_years": q_num(v.get("age_min_years")), "age_max_years": q_num(v.get("age_max_years")),
        "languages": q_arr(v.get("languages") or ["de"]),
        "activity_categories": q_arr(v.get("activity_categories")),
        "price_type": q(v.get("price_type") or "unknown"), "price_text": q(v.get("price_text")),
        "url": q(v.get("url")), "source": q("manual"), "source_url": q(v["source_url"]),
        "retrieved_at": "now()",
    }
    updatable = ["description_en", "i18n", "ends_at", "place_name", "address", "district",
                 "age_min_years", "age_max_years", "languages", "activity_categories", "price_type",
                 "price_text", "url"]
    sets = ["title = excluded.title", "all_day = excluded.all_day"]
    sets += [f"{c} = excluded.{c}" for c in updatable if c in p]
    if provider:
        sets.append("resource_id = coalesce(excluded.resource_id, e.resource_id)")
    sets += ["source = 'manual'", "source_url = excluded.source_url", "retrieved_at = now()"]
    found = "(e.resource_id is not null)" if provider else "null::boolean"
    return (f"-- sheet row {r.number}: {sql_comment(r.label)}\n"
            f"insert into public.family_events as e ({', '.join(cols)})\n"
            f"values ({', '.join(cols.values())})\n"
            f"on conflict (dedupe_key) do update set\n  " + ",\n  ".join(sets) + "\n"
            f"returning {r.number} as sheet_row, (xmax = 0) as added, e.title as name, e.id, {found} as provider_found")


def sql_comment(s: str) -> str:
    return re.sub(r"\s+", " ", s)[:70]


def build_sql(kind: str, rows: list, source_name: str) -> str:
    """One single statement (one data-modifying CTE per row): the CLI only accepts one command per file,
    and a single statement is atomic - either every row is saved or none."""
    target = "public.resources" if kind == "providers" else "public.family_events"
    make = sql_provider if kind == "providers" else sql_event
    ctes = [f"row_{r.number} as (\n{make(r)}\n)" for r in rows]
    extra = ", provider_found" if kind == "events" else ""
    union = "\n  union all ".join(f"select * from row_{r.number}" for r in rows)
    return (f"-- Generated by scripts/import_content.py on {datetime.now():%Y-%m-%d %H:%M} from {sql_comment(source_name)}\n"
            f"-- {len(rows)} {kind} -> {target} (upsert on dedupe_key). Rows with errors are not included.\n"
            f"-- One statement: all rows are saved, or none if anything fails.\n"
            "with\n" + ",\n".join(ctes) + "\n"
            f"select sheet_row, case when added then 'added' else 'updated' end as result, name{extra}\n"
            f"from (\n  {union}\n) t\norder by sheet_row;\n")


# ---------------------------------------------------------------- CSV reading
def read_csv(path: Path):
    notes = []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = path.read_text(encoding="cp1252")
        notes.append("File was not saved as UTF-8 - read it as Windows-1252. If umlauts look wrong, "
                     "download the CSV again from Google Sheets.")
    first = text.splitlines()[0] if text.strip() else ""
    delim = ";" if first.count(";") > first.count(",") else ","
    rows = list(csv.reader(text.splitlines(keepends=True), delimiter=delim))
    return rows, notes


def detect_kind(headers: list) -> str | None:
    hs = {norm_header(h) for h in headers}
    if {"title", "starts at"} <= hs:
        return "events"
    if {"category", "name"} <= hs:
        return "providers"
    return None


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Check a providers/events CSV and turn it into SQL for Supabase.")
    ap.add_argument("csv", help="the CSV file downloaded from Google Sheets")
    ap.add_argument("--type", choices=["providers", "events"], help="file type (normally detected)")
    ap.add_argument("-o", "--out", help="where to write the SQL file")
    ap.add_argument("--apply", action="store_true", help="also run the SQL on the LIVE (linked) database")
    ap.add_argument("--skip-errors", action="store_true", help="with --apply: send good rows despite errors")
    ap.add_argument("--yes", action="store_true", help="with --apply: do not ask for confirmation")
    ap.add_argument("--include-examples", action="store_true", help="also convert EXAMPLE rows (testing only)")
    a = ap.parse_args()

    if a.apply and a.include_examples:
        print("STOP: --include-examples cannot be combined with --apply. Example rows never go to the live database.")
        return 2

    path = Path(a.csv)
    if not path.is_file():
        print(f'STOP: file not found: "{path}"')
        return 2
    table, notes = read_csv(path)
    if not table:
        print("STOP: the file is empty.")
        return 2
    headers = table[0]
    kind = a.type or detect_kind(headers)
    if not kind:
        print("STOP: cannot tell whether this is a providers or an events file. The first row must be the header "
              "row from the template (providers need 'Category' and 'Name', events need 'Title' and 'Starts at').")
        return 2

    hmap = header_map(kind)
    col_field, ignored = {}, []
    for i, h in enumerate(headers):
        f = hmap.get(norm_header(h))
        if f and f not in col_field.values():
            col_field[i] = f
        elif h.strip():
            ignored.append(h.strip())
    missing = [f for f in REQUIRED_HEADERS[kind] if f not in col_field.values()]
    labels = dict(PROVIDER_COLUMNS if kind == "providers" else EVENT_COLUMNS)
    if missing:
        print("STOP: these columns are missing from the header row: " + ", ".join(labels[f] for f in missing))
        return 2

    print(f"Checking {kind} file: {path.name}")
    for n in notes:
        print(f"  NOTE: {n}")
    if ignored:
        print(f"  NOTE: these columns are not used and will be ignored: {', '.join(ignored)}")
    print()

    rows = []
    for idx, cells in enumerate(table[1:], start=2):
        if not any(c.strip() for c in cells):
            continue
        raw = {f: (cells[i] if i < len(cells) else "") for i, f in col_field.items()}
        r = Row(idx, raw)
        main_field = "name" if kind == "providers" else "title"
        r.example = clean(raw.get(main_field)).upper().startswith("EXAMPLE")
        (check_provider if kind == "providers" else check_event)(r)
        rows.append(r)

    # Same key twice in one file -> the later row would silently win; flag it.
    seen = {}
    for r in rows:
        if r.errors:
            continue
        v = r.values
        if kind == "providers":
            key = f"{v['category']}|{v['name'].lower()}|{(v.get('address') or '').lower()}"
        else:
            key = f"{v['title'].lower()}|{v['starts_at']:%Y-%m-%d %H:%M}"
        if key in seen:
            r.err(f"Duplicate of row {seen[key]} (same {'category + name + address' if kind == 'providers' else 'title + start time'})")
        else:
            seen[key] = r.number

    ok, bad, examples = [], [], []
    width = min(48, max([len(r.label) for r in rows] + [10]))
    for r in rows:
        label = (r.label[: width - 3] + "...") if len(r.label) > width else r.label
        if r.example and not a.include_examples:
            status = "SKIPPED (example row - delete it from your sheet)"
            examples.append(r)
        elif r.errors:
            status = "ERROR - not imported"
            bad.append(r)
        else:
            status = "OK" + (" (with warnings)" if r.warnings else "")
            ok.append(r)
            if r.example:
                examples.append(r)
        print(f"Row {r.number:<4} {label:<{width}}  {status}")
        if r.example and not a.include_examples:
            continue
        for e in r.errors:
            print(f"           ERROR: {e}")
        for w in r.warnings:
            print(f"           warning: {w}")

    print()
    print(f"Summary: {len(ok)} ready, {len(bad)} with errors, "
          f"{len([r for r in examples if not a.include_examples])} example rows skipped.")
    if not ok:
        print("Nothing to import - no SQL file written.")
        return 1 if bad else 0

    out = Path(a.out) if a.out else path.with_name(path.stem + ".import.sql")
    out.write_text(build_sql(kind, ok, path.name), encoding="utf-8", newline="\n")
    print(f"SQL written to: {out}")

    if not a.apply:
        if bad:
            print("Fix the rows marked ERROR in your sheet, download the CSV again and re-run this command.")
        else:
            print("All good. To publish, run the same command again with --apply at the end.")
        return 1 if bad else 0

    # ------------------------------------------------------------ --apply (live database)
    if bad and not a.skip_errors:
        print("NOT APPLIED: some rows have errors. Fix them first, or add --skip-errors to send only the OK rows.")
        return 1
    if any(r.example for r in ok):
        print("NOT APPLIED: example rows are never sent to the live database.")
        return 2
    npx = shutil.which("npx")
    if not npx:
        print("NOT APPLIED: 'npx' was not found. Install Node.js (https://nodejs.org) or ask the team to apply "
              f"the SQL file for you: {out}")
        return 1
    if not a.yes:
        if not sys.stdin.isatty():
            print("NOT APPLIED: needs confirmation. Re-run in a terminal, or add --yes.")
            return 1
        answer = input(f"Write {len(ok)} {kind} to the LIVE database now? Type yes to continue: ").strip().lower()
        if answer not in ("yes", "y", "ja"):
            print("Cancelled - nothing was changed.")
            return 1
    cmd = [npx, "-y", "supabase", "db", "query", "--linked", "-f", str(out.resolve())]
    print("Running: npx -y supabase db query --linked -f " + str(out))
    res = subprocess.run(cmd, cwd=REPO_ROOT)
    if res.returncode == 0:
        print(f"Done: {len(ok)} {kind} are now in the live database.")
    else:
        print("The database reported a problem (see above). Nothing was changed - the whole file runs as one "
              "transaction. Send this output to the team.")
    return res.returncode


if __name__ == "__main__":
    sys.exit(main())
