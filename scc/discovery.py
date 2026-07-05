"""Discover a skill corpus and parse each SKILL.md's frontmatter.

A SKILL.md looks like:

    ---
    name: foo
    description: "Do the thing. Use when the user says 'do it'."
    argument-hint: "[optional]"
    ---

    body...

The frontmatter is YAML-ish but simple: one `key: value` per line, values
optionally wrapped in double quotes. Real skill descriptions are long single
lines, so a tiny line parser (no pyyaml, no multi-line values) covers the
whole corpus without a dependency.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

FRONTMATTER_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$")


@dataclass
class Skill:
    name: str
    description: str
    root_label: str          # which root/plugin dir this came from, for display
    path: str
    exists: bool = True

    @property
    def label(self) -> str:
        return self.name or os.path.basename(os.path.dirname(self.path))


@dataclass
class Corpus:
    roots: list[str] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)   # dirs with no SKILL.md, or unparsable


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        inner = value[1:-1]
        return inner.replace('\\"', '"')
    return value


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the leading '---' delimited block into a flat key/value dict.

    Values are read as a single line (real SKILL.md descriptions are one long
    line each); if a value is wrapped in double quotes the quotes are
    stripped. Returns {} if there is no frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = FRONTMATTER_LINE_RE.match(line)
        if not match:
            continue
        key, raw_value = match.group(1), match.group(2)
        fields[key] = _unquote(raw_value)
    return fields


def _read(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def _load_skill(skill_dir: str, root_label: str) -> Skill | None:
    skill_md = os.path.join(skill_dir, "SKILL.md")
    text = _read(skill_md)
    if text is None:
        return None
    fields = parse_frontmatter(text)
    name = fields.get("name") or os.path.basename(skill_dir)
    description = fields.get("description", "")
    return Skill(name=name, description=description, root_label=root_label, path=skill_md)


def discover(roots: list[str]) -> Corpus:
    """Walk each root, one level of subdirectories, loading <dir>/SKILL.md.

    A root may itself be a single skill directory (contains SKILL.md
    directly) - that is treated as a corpus of one.
    """
    corpus = Corpus(roots=list(roots))
    for root in roots:
        if not os.path.isdir(root):
            corpus.skipped.append(f"{root} (not a directory)")
            continue
        root_label = os.path.basename(os.path.normpath(root)) or root

        # a root that is itself a single skill (has SKILL.md directly)
        direct = os.path.join(root, "SKILL.md")
        if os.path.isfile(direct):
            skill = _load_skill(root, root_label)
            if skill:
                corpus.skills.append(skill)
            continue

        for entry in sorted(os.listdir(root)):
            skill_dir = os.path.join(root, entry)
            if not os.path.isdir(skill_dir):
                continue
            skill = _load_skill(skill_dir, root_label)
            if skill is None:
                corpus.skipped.append(os.path.join(root_label, entry))
                continue
            corpus.skills.append(skill)
    return corpus
