#!/usr/bin/env python3
"""Create the docs root, a domain, or a feature folder from the plugin templates.

Usage:
  scaffold.py init  --docs-root docs --product "Acme"            # config + glossary
  scaffold.py feature user-management/user-roles [--code UM-UR] [--title "User roles"] [--docs-root docs] [--gherkin]
Prints the created paths. Never overwrites an existing file.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONFIG_NAME, DOC_FILES, default_code, find_docs_root, load_config,  # noqa: E402
                    render_template, slug_to_title)


def write_new(path: Path, content: str, created: list[Path]) -> None:
    if path.exists():
        print(f"exists, left untouched: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path)


def cmd_init(args: argparse.Namespace) -> int:
    docs_root = Path(args.docs_root).resolve()
    docs_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    product = args.product or docs_root.parent.name
    write_new(docs_root / CONFIG_NAME, render_template("docs-driven.json", {"product_name": product}), created)
    write_new(docs_root / "glossary.md", render_template("glossary.md", {"product_name": product}), created)
    snippet = render_template("CLAUDE-snippet.md", {"docs_root": args.docs_root})
    write_new(docs_root / "CLAUDE-snippet.md", snippet, created)
    for p in created:
        print(f"created: {p}")
    print("next: paste docs/CLAUDE-snippet.md into the project's CLAUDE.md, then edit audience and tone in", CONFIG_NAME)
    return 0


def cmd_feature(args: argparse.Namespace) -> int:
    if "/" not in args.feature:
        print("feature must be given as <domain>/<feature>", file=sys.stderr)
        return 2
    domain, name = args.feature.split("/", 1)
    docs_root = Path(args.docs_root).resolve() if args.docs_root else find_docs_root()
    if docs_root is None:
        print(f"no {CONFIG_NAME} found; run 'scaffold.py init --docs-root docs' first", file=sys.stderr)
        return 2
    config = load_config(docs_root)
    code = args.code or default_code(domain, name)
    title = args.title or slug_to_title(name)
    today = dt.date.today().isoformat()
    values = {"feature": f"{domain}/{name}", "code": code, "title": title, "date": today}
    feat_dir = docs_root / domain / name
    created: list[Path] = []

    domain_dir = docs_root / domain
    domain_code = code.split("-")[0]
    write_new(domain_dir / "overview.md",
              render_template("overview.md", {"domain_title": slug_to_title(domain), "domain_code": domain_code}), created)

    for fname in DOC_FILES:
        write_new(feat_dir / fname, render_template(fname, values), created)
    if args.gherkin or config.get("test_format") == "gherkin":
        write_new(feat_dir / "test-cases.feature", render_template("test-cases.feature", values), created)
    (feat_dir / "assets").mkdir(exist_ok=True)
    write_new(feat_dir / "assets" / ".gitkeep", "", created)

    # register the feature in the domain overview table if not already there
    overview = domain_dir / "overview.md"
    text = overview.read_text(encoding="utf-8")
    row = f"| [{title}]({name}/prod-doc.md) | {code} | draft | |"
    if f"({name}/prod-doc.md)" not in text:
        marker = "| --- | --- | --- | --- |"
        if marker in text:
            text = text.replace(marker, marker + "\n" + row, 1)
        else:
            text += "\n" + row + "\n"
        overview.write_text(text, encoding="utf-8")
        print(f"registered in: {overview}")

    # register the domain in the config
    domains = config.setdefault("domains", {})
    if domain not in domains:
        domains[domain] = ""
        (docs_root / CONFIG_NAME).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        print(f"added domain '{domain}' to {CONFIG_NAME} (fill in its one-line description)")

    for p in created:
        print(f"created: {p}")
    print(f"feature: {domain}/{name}  code: {code}  title: {title}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--docs-root", default="docs")
    p_init.add_argument("--product", default="")
    p_init.set_defaults(func=cmd_init)
    p_feat = sub.add_parser("feature")
    p_feat.add_argument("feature", help="<domain>/<feature> in kebab-case")
    p_feat.add_argument("--code", help="feature code such as UM-UR (capital letters, 1-3 hyphenated tokens)")
    p_feat.add_argument("--title")
    p_feat.add_argument("--docs-root")
    p_feat.add_argument("--gherkin", action="store_true")
    p_feat.set_defaults(func=cmd_feature)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
