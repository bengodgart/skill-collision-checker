"""skill-collision-checker (scc): find trigger-keyword collisions in a
Claude Code skill corpus.

Scans a ~/.claude/skills/*/SKILL.md tree (root overridable, plugin dirs
supported) and flags trigger-keyword collisions between skills, near-duplicate
"when to use" descriptions, and shadowed skills (one skill's triggers a strict
subset of another's). Deterministic, stdlib-only, offline, keyword/phrase
overlap based (no embeddings). Suggest-only: it never edits a SKILL.md. See
README.md.
"""

from __future__ import annotations

__version__ = "0.1.0"
