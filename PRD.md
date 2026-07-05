# PRD — skill-collision-checker (scc)

**One-liner (from brief 09):** A non-interactive linter that scans a `~/.claude/skills/*/SKILL.md` corpus (or a plugin's skills) and flags **trigger-keyword collisions** - two skills that fire on the same words - plus near-duplicate "when to use" lines and coverage gaps, outputting a KEEP / TUNE table, for any Claude Code power user whose growing skill library makes "why did the wrong skill fire?" a real, undebugged problem.

**Usefulness (from brief 09):** Skill matching is genuinely ambiguous - the platform either picks the best match silently or asks which skill to use, and with many installed skills that silent pick goes wrong. Ben has 30+ real skills and already hand-wrote a `/skill-audit` skill just to catch this. The unfilled slice: no public tool statically analyzes a skill corpus for trigger-keyword collisions and coverage gaps. Ships with a bundled example skills set so a stranger sees a real collision report in under 2 minutes.

## v1 scope (capped)

1. Discover skills: parse frontmatter (`name`, `description`) from every `SKILL.md` under a root (default `~/.claude/skills`, overridable), plus any `--plugin` dirs.
2. Extract trigger signals per skill, from the description only: quoted trigger phrases (`'take a note'`), keywords (stopword-filtered content words), and the normalized full text for wording comparisons. Slash-command examples (`'/foo --flag'`) feed keywords via full-text tokenization but are excluded from the phrase set, since a skill's own invocation name is never itself a shared "trigger."
3. Pairwise collision score: shared trigger phrases (each one a strong signal) plus a keyword Jaccard; pairs at or above `--threshold` (default 0.3) are a COLLISION with the exact overlapping tokens shown.
4. Shadow detection: skill B's full trigger surface (phrases + keywords) is a non-empty strict subset of skill A's -> B is redundant next to A, flagged TUNE with a specific suggestion ("narrow B's trigger; it is shadowed by A"). A shadow pair is not also double-counted as a collision.
5. Near-duplicate wording: full-description text-similarity ratio (difflib) at or above `--near-ratio` (default 0.85), independent of the phrase/keyword checks - catches two skills paraphrased close to identically.
6. One disposition per skill: KEEP / TUNE / COLLISION, precedence shadow > collision > near-duplicate > keep. Report: terminal text always, `--md` and `--html` optional.
7. README opens with a real finding from Ben's own 31-skill corpus (read-only; nothing in `~/.claude/skills` is ever written).

## Non-goals (NOT v1 - expansion paths, parked)

- Auto-editing SKILL.md files. Suggest-only, per the trust rule - it names the fix, it never applies one.
- Semantic-embedding similarity. Deterministic keyword/phrase overlap only, so a fresh clone reproduces the exact same report every run.
- Coverage-gap detection against Ben's actual workflow history (that needs the memory corpus, which is not something a public tool should read). The brief's "coverage gaps" line is descriptive of the broader pain (from `/skill-audit`'s scope); this tool's v1 is the collision/shadow/near-dup slice only, capped per the non-goals in brief 09 itself ("a new pain point is a feature of an existing app, not a new SaaS" - scope stays narrow).
- Running or invoking skills. It only reads `SKILL.md` text.
- A hosted service, accounts.

## Demo path (stranger sees value in under 2 minutes)

Clone -> `python -m scc check fixtures/skills` -> see 2 COLLISION, 3 TUNE (2 shadowed, 1 near-duplicate), 3 KEEP, with the exact shared trigger phrase (`'capture an idea'`) and shared keywords named. Then `python -m scc check ~/.claude/skills` audits their own real corpus instantly, at $0, offline.

## Done when

- The CLI produces a KEEP/TUNE/COLLISION table on the bundled fixtures in under 2 minutes for a fresh clone.
- The planted collision pair (`note-taker` / `quick-capture`) and at least one planted shadowed pair (`set-reminder` shadowed by `broad-reminder`) are reproduced.
- At least one real collision pair from Ben's own skills corpus is reproduced with the overlapping tokens shown (pasted in EVIDENCE.md and the README).
- Every COLLISION row names the shared trigger tokens; every TUNE row carries a specific suggestion.
- README opens with a real finding; copy passes the no-em-dash sweep. Repo public, MIT, $0, no network.
