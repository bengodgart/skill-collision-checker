# Parking lot - skill-collision-checker

Ideas that surfaced during the v1 build. NOT in v1 scope.

- **Semantic-embedding collision mode** - an opt-in v2 mode using embeddings for phrasing that shares no words at all. Keep the deterministic keyword/phrase mode as the default; the whole point of v1 is a report that never changes between runs.
- **Coverage-gap detection** - flagging a recurring workflow with no skill at all needs the user's own workflow history (memory corpus), which a public tool should not read. `/skill-audit` already does this for Ben's own setup; this piece stays scoped to the corpus that is actually on disk.
- **Auto-tune mode** - apply the suggested description narrowing directly, with a diff and confirmation. Only ever suggest-first; writing to a user's SKILL.md is a data-safety-gated action, same line `claude-context-audit` draws for CLAUDE.md.
- **GitHub Action** - fail a plugin PR if a new skill collides with an existing trigger. Natural CI hook once the CLI is stable; not needed for a portfolio v1.
- **Wire into claude-context-audit** - one combined view showing token cost AND collision risk per skill. Keep them separate pieces per that project's own parking_lot.md; revisit only if both get real usage.

Product-creep tripwire (doctrine T11): a hosted scanner with accounts, or an "auto-fix my skills" service, is an app. Stop and park.
