#!/usr/bin/env python3
"""Print a markdown table of every feature with per-document status and coverage numbers.

Usage: status_report.py [--docs-root docs]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DOC_FILES, discover_features, find_docs_root, requirement_ids, test_cases  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs-root")
    args = ap.parse_args()
    docs_root = Path(args.docs_root).resolve() if args.docs_root else find_docs_root()
    if docs_root is None:
        print("docs root not found", file=sys.stderr)
        return 2
    print("| Feature | Code | prod | user | tests | tech | Reqs | Cases |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for f in discover_features(docs_root):
        reqs = {r: i for r, i in requirement_ids(f.docs.get("prod-doc.md", ({}, ""))[1]).items() if not i["deprecated"]}
        cases = test_cases(f.docs.get("test-cases.md", ({}, ""))[1])
        cols = " | ".join(f.status(d) for d in DOC_FILES)
        print(f"| {f.key} | {f.code} | {cols} | {len(reqs)} | {len(cases)} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
