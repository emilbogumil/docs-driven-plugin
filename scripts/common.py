"""Shared helpers for the docs-driven scripts. Standard library only."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = "docs-driven.json"
DOC_FILES = ("prod-doc.md", "user-doc.md", "test-cases.md", "tech-doc.md")
STATUSES = ("draft", "approved", "current", "deprecated")
CASE_TYPES = ("automated", "planned", "manual")
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# A feature code is 1-3 tokens of capital letters joined by hyphens, e.g. UM-UR.
# Keeping tokens letters-only means "-R01" / "-T01" / "-D01" can never be confused with the code.
CODE_RE = r"[A-Z]+(?:-[A-Z]+){0,2}"
ID_RE = re.compile(rf"\b(?P<code>{CODE_RE})-(?P<kind>[RTD])(?P<num>\d{{2,}})\b")
REQ_HEADING_RE = re.compile(rf"^###\s+(?P<id>{CODE_RE}-R\d{{2,}})\s*:\s*(?P<title>.*?)\s*$", re.M)
TC_HEADING_RE = re.compile(rf"^###\s+(?P<id>{CODE_RE}-T\d{{2,}})\s*:\s*(?P<title>.*?)\s*$", re.M)
COVERS_RE = re.compile(r"^\s*-\s*\*\*Covers:\*\*\s*(?P<ids>.*)$", re.M)
TYPE_RE = re.compile(r"^\s*-\s*\*\*Type:\*\*\s*(?P<type>\w+)", re.M)
AUTOMATED_IN_RE = re.compile(r"^\s*-\s*\*\*Automated in:\*\*\s*(?P<path>\S.*)?$", re.M)
HTML_COVERS_RE = re.compile(r"<!--\s*covers:\s*(?P<ids>[^>]*)-->")
GHERKIN_TAGS_RE = re.compile(r"^\s*((?:@\S+\s*)+)$", re.M)
DEPRECATED_RE = re.compile(r"^Deprecated on ", re.M)
GUIDE_RE = re.compile(r"<!--\s*guide:")
OVERVIEW_ROW_RE = re.compile(r"^\|\s*\[[^\]]*\]\((?P<feature>[^)/]+)/prod-doc\.md\)\s*\|\s*(?P<code>[^|]*)\|\s*(?P<status>[^|]*)\|", re.M)


def find_docs_root(start: Path | None = None) -> Path | None:
    """Walk up from start looking for docs-driven.json, directly or in a docs/ subfolder."""
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / CONFIG_NAME).is_file():
            return candidate
        if (candidate / "docs" / CONFIG_NAME).is_file():
            return candidate / "docs"
    return None


def load_config(docs_root: Path) -> dict:
    path = docs_root / CONFIG_NAME
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a flat YAML frontmatter block: scalars and simple [a, b] or '- item' lists."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4 :]
    data: dict = {}
    current_list_key = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and current_list_key and line.lstrip().startswith("- "):
            data[current_list_key].append(line.lstrip()[2:].strip())
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_list_key = key
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
        else:
            data[key] = value.strip("'\"")
    # keys that stayed empty lists but were meant as empty scalars
    for key in list(data):
        if data[key] == [] and key not in ("related_prs", "tags"):
            data[key] = ""
    return data, body


def render_template(name: str, values: dict) -> str:
    text = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() if i == 0 else w for i, w in enumerate(slug.replace("_", "-").split("-")))


def default_code(domain: str, feature: str) -> str:
    def part(slug: str) -> str:
        words = [w for w in slug.replace("_", "-").split("-") if w]
        if len(words) >= 2:
            return "".join(w[0] for w in words).upper()
        return words[0][:4].upper() if words else "X"

    return f"{part(domain)}-{part(feature)}"


@dataclass
class Feature:
    domain: str
    name: str
    path: Path
    docs: dict = field(default_factory=dict)  # filename -> (frontmatter, body)

    @property
    def key(self) -> str:
        return f"{self.domain}/{self.name}"

    @property
    def code(self) -> str:
        for fm, _ in self.docs.values():
            if fm.get("code"):
                return fm["code"]
        return ""

    def status(self, doc: str) -> str:
        fm = self.docs.get(doc, ({}, ""))[0]
        return fm.get("status", "missing") if fm else "missing"


def discover_features(docs_root: Path) -> list[Feature]:
    """A feature is any <docs_root>/<domain>/<feature>/ folder holding at least one of the four docs."""
    features: list[Feature] = []
    for domain_dir in sorted(p for p in docs_root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
        for feat_dir in sorted(p for p in domain_dir.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
            docs = {}
            for name in DOC_FILES:
                f = feat_dir / name
                if f.is_file():
                    docs[name] = parse_frontmatter(f.read_text(encoding="utf-8"))
            if docs:
                features.append(Feature(domain_dir.name, feat_dir.name, feat_dir, docs))
    return features


def requirement_ids(prod_body: str) -> dict[str, dict]:
    """Return {id: {title, deprecated}} for every requirement heading in a prod-doc body."""
    result: dict[str, dict] = {}
    matches = list(REQ_HEADING_RE.finditer(prod_body))
    for i, m in enumerate(matches):
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(prod_body)
        section = prod_body[m.end() : section_end]
        result[m.group("id")] = {
            "title": m.group("title"),
            "deprecated": bool(DEPRECATED_RE.search(section)),
        }
    return result


def test_cases(tc_body: str) -> dict[str, dict]:
    """Return {id: {title, covers, type, automated_in}} from a test-cases.md body."""
    result: dict[str, dict] = {}
    matches = list(TC_HEADING_RE.finditer(tc_body))
    for i, m in enumerate(matches):
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(tc_body)
        section = tc_body[m.end() : section_end]
        covers_m = COVERS_RE.search(section)
        covers = ID_RE.findall(covers_m.group("ids")) if covers_m else []
        type_m = TYPE_RE.search(section)
        auto_m = AUTOMATED_IN_RE.search(section)
        result[m.group("id")] = {
            "title": m.group("title"),
            "deprecated": bool(DEPRECATED_RE.search(section)),
            "covers": [f"{c}-{k}{n}" for c, k, n in covers if k == "R"],
            "type": (type_m.group("type").lower() if type_m else ""),
            "automated_in": (auto_m.group("path") or "").strip() if auto_m else "",
        }
    return result


def gherkin_cases(feature_text: str) -> dict[str, dict]:
    """Return {case_id: {covers}} from tag lines in a .feature file."""
    result: dict[str, dict] = {}
    for m in GHERKIN_TAGS_RE.finditer(feature_text):
        tags = [t.lstrip("@") for t in m.group(1).split()]
        ids = [t for t in tags if ID_RE.fullmatch(t)]
        cases = [t for t in ids if ID_RE.fullmatch(t).group("kind") == "T"]
        reqs = [t for t in ids if ID_RE.fullmatch(t).group("kind") == "R"]
        for case in cases:
            result.setdefault(case, {"covers": []})["covers"].extend(reqs)
    return result


SKIP_DIRS = {".git", "node_modules", "dist", "build", "coverage", ".next", "target", "__pycache__", ".venv", "venv", "vendor"}
CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".rs", ".java", ".kt", ".cs", ".php", ".swift", ".feature", ".sql", ".vue", ".svelte"}


def scan_code_for_ids(code_root: Path, docs_root: Path, kinds: str = "T") -> dict[str, list[str]]:
    """Map every CODE-Tnn (or Rnn) id found in source files to the files mentioning it."""
    found: dict[str, list[str]] = {}
    docs_root = docs_root.resolve()
    for dirpath, dirnames, filenames in os.walk(code_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not Path(dirpath, d).resolve() == docs_root]
        for fn in filenames:
            p = Path(dirpath, fn)
            if p.suffix not in CODE_SUFFIXES:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in ID_RE.finditer(text):
                if m.group("kind") in kinds:
                    rel = os.path.relpath(p, code_root)
                    lst = found.setdefault(m.group(0), [])
                    if rel not in lst:
                        lst.append(rel)
    return found


def resolve_code_root(docs_root: Path, config: dict) -> Path:
    return (docs_root / config.get("code_root", "..")).resolve()
