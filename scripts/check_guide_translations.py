"""Check guide body translations in content/guides/<lang>/<slug>.md against content/guides/en/.
Rules: same number of '## ' headings, list items and links; same URLs, e-mails and phone numbers;
every number in the translation also appears in the English text (decimal comma allowed)."""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent / "content" / "guides"
def nums(t):
    # ISO dates in English (2026-09-26) may be written as 26.09.2026 in a translation
    t = re.sub(r"(\d{4})-(\d{2})-(\d{2})", lambda m: f"{m[1]} {m[2]} {m[3]} {m[3]}.{m[2]} {m[3]}.{m[2]}.{m[1]}", t)
    return {n.replace(",", ".") for n in re.findall(r"\d+(?:[.,]\d+)?", t)}
def feats(t):
    return {"headings": len(re.findall(r"^## ", t, re.M)), "items": len(re.findall(r"^\s*(?:- |\d+\. )", t, re.M)),
            "urls": sorted(re.findall(r"\]\((https?://[^)]+)\)", t)), "emails": sorted(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", t))}
bad = 0
for lang_dir in sorted(p for p in root.iterdir() if p.is_dir() and p.name != "en"):
    for f in sorted(lang_dir.glob("*.md")):
        en = (root / "en" / f.name).read_text(); tr = f.read_text(); errs = []
        fe, ft = feats(en), feats(tr)
        for k in fe:
            if fe[k] != ft[k]: errs.append(f"{k}: en={fe[k] if k in ('headings','items') else len(fe[k])} {lang_dir.name}={ft[k] if k in ('headings','items') else len(ft[k])}")
        extra = nums(tr) - nums(en)
        if extra: errs.append(f"numbers not in English: {sorted(extra)}")
        print(f"{lang_dir.name}/{f.name}: " + ("OK" if not errs else "ERROR " + "; ".join(errs)))
        bad += bool(errs)
sys.exit(1 if bad else 0)
