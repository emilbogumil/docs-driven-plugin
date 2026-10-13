#!/usr/bin/env python3
"""Check consistency of docs-driven feature folders and their traceability into code.

Usage:
  trace_check.py [--docs-root docs] [--feature domain/feature] [--json] [--matrix] [--write-matrix] [--strict]

Checks per feature:
  structure   the four files exist, frontmatter parses, code and status are valid and agree across files,
              no template guide comments remain once a document leaves draft
  questions   an approved or current prod-doc has no Open questions row without an owner (every open question
              must have been asked in a grilling round before sign-off; resolved and deferred ones leave the table)
  ids         requirement and case IDs use the feature's code, are unique, and are not skipped
  coverage    every live requirement has a case; every case covers an existing requirement (feature or domain-wide)
  user-doc    every <!-- covers: --> comment names existing requirements
  automation  cases marked automated are found in source files by ID (a named file that exists is weaker evidence);
              planned cases must become automated or manual before the feature is current
  status      a doc marked current while the prod-doc is still draft, overview row disagreeing with the prod-doc,
              or a current document past its review date
Exit code 1 when any error is found (warnings do not fail unless --strict).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CASE_TYPES, DOC_FILES, GUIDE_RE, HTML_COVERS_RE, ID_RE, OVERVIEW_ROW_RE, STATUSES, Feature,  # noqa: E402
                    discover_features, find_docs_root, gherkin_cases, load_config, requirement_ids,
                    resolve_code_root, scan_code_for_ids, test_cases)


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def error(self, feature: str, check: str, msg: str) -> None:
        self.items.append({"level": "error", "feature": feature, "check": check, "message": msg})

    def warn(self, feature: str, check: str, msg: str) -> None:
        self.items.append({"level": "warning", "feature": feature, "check": check, "message": msg})

    def count(self, level: str) -> int:
        return sum(1 for i in self.items if i["level"] == level)


def domain_rules(docs_root: Path, domain: str) -> dict[str, dict]:
    """Domain-wide requirements declared in <domain>/overview.md, e.g. UM-R01."""
    overview = docs_root / domain / "overview.md"
    if not overview.is_file():
        return {}
    return requirement_ids(overview.read_text(encoding="utf-8"))


def overview_statuses(docs_root: Path, domain: str) -> dict[str, str]:
    overview = docs_root / domain / "overview.md"
    if not overview.is_file():
        return {}
    text = overview.read_text(encoding="utf-8")
    return {m.group("feature").strip(): m.group("status").strip() for m in OVERVIEW_ROW_RE.finditer(text)}


def id_list(ids: list[str], limit: int = 8) -> str:
    ids = sorted(ids)
    shown = ", ".join(ids[:limit])
    return shown + (f" and {len(ids) - limit} more" if len(ids) > limit else "")


def matrix_table(matrix: dict[str, list[str]]) -> str:
    rows = ["| Requirement | Cases |", "| --- | --- |"]
    rows += [f"| {r} | {', '.join(cs) or '(none)'} |" for r, cs in matrix.items()]
    return "\n".join(rows)


def write_matrix(feat: Feature, matrix: dict[str, list[str]]) -> bool:
    """Replace the table under '## Coverage' in test-cases.md. Returns True when the file changed."""
    path = feat.path / "test-cases.md"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## Coverage[ \t]*$", text, re.M)
    if not m:
        return False
    start = m.end()
    nxt = re.search(r"^## ", text[start:], re.M)
    end = start + nxt.start() if nxt else len(text)
    section = text[start:end]
    # keep any non-table prose (e.g. guide comments) that precedes the table
    prose = "\n".join(l for l in section.splitlines() if l.strip() and not l.lstrip().startswith("|"))
    new_section = "\n\n" + (prose + "\n\n" if prose else "") + matrix_table(matrix) + "\n\n"
    new_text = text[:start] + new_section + text[end:]
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def unasked_open_questions(body: str) -> list[str]:
    """Rows of the Open questions table with an empty Owner cell (never asked or never assigned)."""
    m = re.search(r"^## Open questions\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.strip().startswith("|") or len(cells) < 3 or cells[0] in ("Question", "") or set(cells[0]) <= set("-: "):
            continue
        if not cells[1]:
            rows.append(cells[0])
    return rows


def check_feature(feat: Feature, config: dict, code_root: Path, code_ids: dict[str, list[str]], rep: Report,
                  today: dt.date, domain_reqs: dict[str, dict], overview_status: str | None) -> dict:
    key = feat.key
    # structure
    for fname in DOC_FILES:
        if fname not in feat.docs:
            rep.error(key, "structure", f"missing {fname}")
    codes = set()
    for fname, (fm, body) in feat.docs.items():
        if not fm:
            rep.error(key, "structure", f"{fname}: no frontmatter")
            continue
        if fm.get("feature") != key:
            rep.error(key, "structure", f"{fname}: frontmatter feature is '{fm.get('feature')}', folder is '{key}'")
        if fm.get("status") not in STATUSES:
            rep.error(key, "structure", f"{fname}: status '{fm.get('status')}' is not one of {', '.join(STATUSES)}")
        if fm.get("code"):
            codes.add(fm["code"])
        else:
            rep.error(key, "structure", f"{fname}: missing code")
        guides = len(GUIDE_RE.findall(body))
        if guides and fm.get("status") in ("approved", "current"):
            (rep.error if fm.get("status") == "current" else rep.warn)(
                key, "structure", f"{fname}: {guides} template guide comment(s) still present; delete them before publishing")
    prod_doc = feat.docs.get("prod-doc.md")
    if prod_doc and prod_doc[0].get("status") in ("approved", "current"):
        unasked = unasked_open_questions(prod_doc[1])
        if unasked:
            rep.error(key, "questions", f"prod-doc.md: {len(unasked)} open question(s) without an owner; "
                      f"ask them in a grilling round before sign-off: " + "; ".join(q[:60] for q in unasked))
    if len(codes) > 1:
        rep.error(key, "structure", f"files disagree on the feature code: {', '.join(sorted(codes))}")
    code = feat.code

    prod_fm, prod_body = feat.docs.get("prod-doc.md", ({}, ""))
    tc_fm, tc_body = feat.docs.get("test-cases.md", ({}, ""))
    user_fm, user_body = feat.docs.get("user-doc.md", ({}, ""))
    tech_fm = feat.docs.get("tech-doc.md", ({}, ""))[0]
    implemented = prod_fm.get("status") == "current" or tech_fm.get("status") == "current"

    # ids
    reqs = requirement_ids(prod_body)
    cases = test_cases(tc_body)
    feature_file = feat.path / "test-cases.feature"
    if feature_file.is_file():
        for cid, info in gherkin_cases(feature_file.read_text(encoding="utf-8")).items():
            entry = cases.setdefault(cid, {"title": "(gherkin)", "covers": [], "type": "automated",
                                           "automated_in": feature_file.name, "deprecated": False})
            entry["gherkin"] = True
            for r in info["covers"]:
                if r not in entry["covers"]:
                    entry["covers"].append(r)

    def check_numbering(ids: list[str], kind: str) -> None:
        nums = []
        for i in ids:
            m = ID_RE.fullmatch(i)
            if not m:
                continue
            if code and m.group("code") != code:
                rep.error(key, "ids", f"{i} uses code '{m.group('code')}' but the feature code is '{code}'")
            nums.append(int(m.group("num")))
        if nums:
            missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
            if missing:
                rep.warn(key, "ids", f"{kind} numbering skips {id_list([f'{code}-{kind}{n:02d}' for n in missing])}")

    check_numbering(list(reqs), "R")
    check_numbering(list(cases), "T")
    if not reqs:
        rep.warn(key, "ids", "prod-doc has no requirements yet")

    # coverage
    live_reqs = {r for r, info in reqs.items() if not info["deprecated"]}
    covered: dict[str, list[str]] = {r: [] for r in reqs}
    live_cases = {cid: info for cid, info in cases.items() if not info.get("deprecated")}
    for cid, info in live_cases.items():
        if not info["covers"]:
            rep.error(key, "coverage", f"{cid} does not state which requirements it covers")
        for r in info["covers"]:
            if r in reqs:
                covered[r].append(cid)
            elif r not in domain_reqs:
                rep.error(key, "coverage", f"{cid} covers {r}, which does not exist in prod-doc or the domain overview")
        if info["type"] and info["type"] not in CASE_TYPES:
            rep.error(key, "coverage", f"{cid}: type must be one of {', '.join(CASE_TYPES)}, got '{info['type']}'")
    untyped = [cid for cid, info in live_cases.items() if not info["type"]]
    if untyped:
        rep.warn(key, "coverage", f"no Type line on {id_list(untyped)}")
    uncovered = sorted(r for r in live_reqs if not covered[r])
    for r in uncovered:
        rep.error(key, "coverage", f"{r} has no test case")

    # user-doc
    for m in HTML_COVERS_RE.finditer(user_body):
        for c, k, n in ID_RE.findall(m.group("ids")):
            rid = f"{c}-{k}{n}"
            if rid not in reqs and rid not in domain_reqs:
                rep.error(key, "user-doc", f"user-doc references {rid}, which does not exist in prod-doc or the domain overview")

    # automation
    automated = {cid for cid, info in live_cases.items() if info["type"] == "automated"}
    planned = sorted(cid for cid, info in live_cases.items() if info["type"] == "planned")
    found, named_only, missing = [], [], []
    for cid in sorted(automated):
        if live_cases[cid].get("gherkin") or cid in code_ids:
            found.append(cid)
            continue
        paths = [part.strip().split()[0].rstrip(",;") for part in live_cases[cid]["automated_in"].split(",") if part.strip()]
        if paths and any((code_root / pt).exists() for pt in paths):
            named_only.append(cid)
        else:
            missing.append(cid)
    if named_only:
        rep.warn(key, "automation", f"{len(named_only)} automated case(s) name a test file but the file does not carry "
                                    f"their ID yet: {id_list(named_only)}")
    if missing:
        (rep.error if implemented else rep.warn)(
            key, "automation", f"{len(missing)} automated case(s) are found in no source file: {id_list(missing)}")
    if planned:
        (rep.error if implemented else rep.warn)(
            key, "automation", f"{len(planned)} planned case(s) still need a test or a manual decision: {id_list(planned)}")
    for found_id, files in code_ids.items():
        if code and found_id.startswith(code + "-T") and found_id not in cases:
            rep.error(key, "automation", f"source mentions {found_id} but test-cases.md has no such case ({', '.join(files[:3])})")

    # status
    prod_status = prod_fm.get("status", "")
    for fname, (fm, _) in feat.docs.items():
        if fname != "prod-doc.md" and fm.get("status") == "current" and prod_status in ("draft", ""):
            rep.error(key, "status", f"{fname} is current but prod-doc is still draft")
    if prod_status == "current" and user_fm and user_fm.get("status") == "draft":
        rep.warn(key, "status", "prod-doc is current but user-doc is still draft; publish or deprecate it")
    if overview_status is None:
        rep.warn(key, "status", "feature has no row in the domain overview.md")
    elif prod_status and overview_status != prod_status:
        rep.warn(key, "status", f"overview.md row says '{overview_status}' but prod-doc is '{prod_status}'")
    review_days = int(config.get("review_after_days", 0) or 0)
    for fname, (fm, _) in feat.docs.items():
        lr = fm.get("last_reviewed", "")
        try:
            when = dt.date.fromisoformat(lr) if lr else None
        except ValueError:
            rep.error(key, "status", f"{fname}: last_reviewed '{lr}' is not an ISO date")
            continue
        if review_days and when and (today - when).days > review_days and fm.get("status") == "current":
            rep.warn(key, "status", f"{fname} was last reviewed {lr}, more than {review_days} days ago")

    return {
        "feature": key,
        "code": code,
        "requirements": len(reqs),
        "live_requirements": len(live_reqs),
        "cases": len(live_cases),
        "automated_cases": len(automated),
        "automated_found": len(found),
        "planned_cases": len(planned),
        "uncovered": uncovered,
        "matrix": {r: sorted(c) for r, c in covered.items()},
        "statuses": {f: feat.status(f) for f in DOC_FILES},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs-root")
    ap.add_argument("--feature", help="limit to one domain/feature")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--matrix", action="store_true", help="print the coverage table in markdown")
    ap.add_argument("--write-matrix", action="store_true", help="replace the table under '## Coverage' in test-cases.md")
    ap.add_argument("--strict", action="store_true", help="warnings also fail")
    args = ap.parse_args()

    docs_root = Path(args.docs_root).resolve() if args.docs_root else find_docs_root()
    if docs_root is None or not docs_root.is_dir():
        print("docs root not found; pass --docs-root or create docs-driven.json", file=sys.stderr)
        return 2
    config = load_config(docs_root)
    code_root = resolve_code_root(docs_root, config)
    rep = Report()
    features = discover_features(docs_root)
    if args.feature:
        features = [f for f in features if f.key == args.feature]
        if not features:
            print(f"feature {args.feature} not found under {docs_root}", file=sys.stderr)
            return 2
    code_ids = scan_code_for_ids(code_root, docs_root) if code_root.is_dir() else {}
    today = dt.date.today()
    summaries = []
    for f in features:
        ov = overview_statuses(docs_root, f.domain)
        summaries.append(check_feature(f, config, code_root, code_ids, rep, today, domain_rules(docs_root, f.domain), ov.get(f.name)))
        if args.write_matrix and write_matrix(f, summaries[-1]["matrix"]):
            print(f"updated coverage table in {f.path / 'test-cases.md'}")

    if args.json:
        print(json.dumps({"docs_root": str(docs_root), "features": summaries, "findings": rep.items}, indent=2))
    else:
        for s in summaries:
            st = " ".join(f"{k.split('-')[0]}={v}" for k, v in s["statuses"].items())
            planned = f" planned={s['planned_cases']}" if s["planned_cases"] else ""
            print(f"{s['feature']} [{s['code']}]  reqs={s['live_requirements']} cases={s['cases']} "
                  f"automated={s['automated_found']}/{s['automated_cases']}{planned}  {st}")
            if args.matrix:
                print(matrix_table(s["matrix"]) + "\n")
        for item in rep.items:
            print(f"{item['level'].upper():7} {item['feature']}  {item['check']}: {item['message']}")
        print(f"\n{len(summaries)} feature(s), {rep.count('error')} error(s), {rep.count('warning')} warning(s)")
    failed = rep.count("error") > 0 or (args.strict and rep.count("warning") > 0)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
