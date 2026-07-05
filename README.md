# skill-collision-checker

**I ran it on my 31 Claude Code skills and found a real collision on the first try.** `sync-plugins` and `sync-skills` share 32 keywords in their descriptions (jaccard 0.74) because they are near-mirror templated skills - one manages plugins, the other manages skills, and the wording barely changed between them.

```
$ python -m scc check ~/.claude/skills

Skill collision check
skills scanned: 31   threshold: 0.30   near-dup ratio: 0.85

Disposition: 29 KEEP, 0 TUNE, 2 COLLISION

  COLLISION  sync-plugins   collides with sync-skills (shared: add, additional, alone,
                             already, authoritative, between, +26 more; jaccard 0.74)
  COLLISION  sync-skills    collides with sync-plugins (shared: add, additional, alone,
                             already, authoritative, between, +26 more; jaccard 0.74)
  KEEP       build-apps     -
  ...
```

That is a real run, read-only, against my own setup. Full output is in [`EVIDENCE.md`](EVIDENCE.md).

Claude Code either picks the best-matching skill silently or asks which one you meant, and once a library has 30+ skills that silent pick starts going wrong. Nothing public statically checks a skill corpus for this. So I wrote the checker.

## Quickstart (3 commands)

```bash
git clone https://github.com/bengodgart/skill-collision-checker
cd skill-collision-checker
python -m scc check fixtures/skills
```

Then run it against your own: `python -m scc check ~/.claude/skills`. Python 3.9+ (standard library only, nothing to install).

## What it reports

- **Collisions** - two skills that fire on the same words: shared quoted trigger phrases (`'take a note'`) plus a keyword Jaccard score, above a threshold. Every COLLISION row names the exact shared tokens.
- **Shadowed skills** - one skill's whole trigger surface is a strict subset of another's, so it never fires when the broader one would not also fire. Flagged TUNE with a specific suggestion: "narrow X's trigger; it is shadowed by Y."
- **Near-duplicate wording** - two descriptions that read almost the same, independent of shared words, caught with a text-similarity ratio.
- One disposition per skill: **KEEP / TUNE / COLLISION**, terminal always, `--md` and `--html` optional.

## The bundled example

`fixtures/skills/` ships 8 fake skills with a planted collision (`note-taker` / `quick-capture`, sharing the phrase `'capture an idea'`) and a planted shadow (`set-reminder` shadowed by `broad-reminder`). Run `python -m scc check fixtures/skills` and both show up, plus a near-duplicate wording pair the algorithm found on its own. Full report: [`examples/sample-report.txt`](examples/sample-report.txt) ([HTML](examples/sample-report.html), [Markdown](examples/sample-report.md)).

## Options

```
python -m scc check [root] [--plugin PATH ...] [--threshold F] [--near-ratio F] [--html PATH] [--md PATH] [--quiet]
```

- `root` - a directory of skill folders, or a single skill's own folder. Defaults to `~/.claude/skills`.
- `--plugin PATH` - an additional skills directory to include (repeatable) - point it at a plugin's skills folder alongside your main root.
- `--threshold` - collision score threshold, 0 to 1 (default 0.3). Lower catches more, and more false positives.
- `--near-ratio` - text-similarity ratio for near-duplicate wording (default 0.85).

## Suggest-only, on purpose

It never edits a `SKILL.md`. It tells you which two skills are fighting, over which exact words, and what a fix could look like; the edit stays yours. Same trust line `claude-context-audit` draws for `CLAUDE.md`.

## Deterministic, not semantic

Collisions are scored on quoted trigger phrases and a keyword Jaccard, not embeddings. Same corpus, same flags, same report, every run, no network call, no model. Semantic similarity for phrasing that shares no words at all is a v2 expansion path (see `parking_lot.md`), off by default.

## Tests

```bash
python -m pytest tests/ -v   # 22 tests, no network, bundled fixtures only
```

## Why I built it

I have 30+ custom skills and had already hand-written a `/skill-audit` skill just to catch "why did the wrong skill fire." That was proof enough the pain was real, but it only runs inside a Claude session and never gives me a portable, checkable report. So I built the standalone version: point it at any skills directory, get back the exact overlapping words, offline, in one command.

## License

MIT. See [LICENSE](LICENSE).
