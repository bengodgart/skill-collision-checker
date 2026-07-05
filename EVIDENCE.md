# Evidence — skill-collision-checker

Ship-gate evidence: pasted terminal output with exit codes, not assertions. Environment: `C:\Users\Asus PC\AppData\Local\Programs\Python\Python314\python.exe`, Python 3.14.4, pytest 9.1.1.

## 1. Test suite

Command: `python -m pytest tests/ -v`

```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Asus PC\AppData\Local\Programs\Python\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\dev\skill-collision-checker
configfile: pyproject.toml
collecting ... collected 22 items

tests/test_scc.py::test_parse_frontmatter_quoted_value PASSED            [  4%]
tests/test_scc.py::test_parse_frontmatter_unquoted_value PASSED          [  9%]
tests/test_scc.py::test_parse_frontmatter_no_block_returns_empty PASSED  [ 13%]
tests/test_scc.py::test_discover_finds_all_fixture_skills PASSED         [ 18%]
tests/test_scc.py::test_discover_missing_root_is_skipped_not_fatal PASSED [ 22%]
tests/test_scc.py::test_extract_signals_quoted_phrases PASSED            [ 27%]
tests/test_scc.py::test_extract_signals_keywords_drop_stopwords PASSED   [ 31%]
tests/test_scc.py::test_extract_signals_no_quotes_still_gets_keywords PASSED [ 36%]
tests/test_scc.py::test_collision_score_shared_phrase_dominates PASSED   [ 40%]
tests/test_scc.py::test_collision_score_disjoint_is_zero PASSED          [ 45%]
tests/test_scc.py::test_planted_collision_note_taker_quick_capture PASSED [ 50%]
tests/test_scc.py::test_planted_shadow_set_reminder_by_broad_reminder PASSED [ 54%]
tests/test_scc.py::test_shadowed_pair_not_also_double_counted_as_collision PASSED [ 59%]
tests/test_scc.py::test_disposition_table_covers_every_skill_exactly_once PASSED [ 63%]
tests/test_scc.py::test_set_reminder_disposition_is_tune_with_suggestion PASSED [ 68%]
tests/test_scc.py::test_note_taker_disposition_is_collision_with_shared_tokens PASSED [ 72%]
tests/test_scc.py::test_clean_skills_are_kept PASSED                     [ 77%]
tests/test_scc.py::test_near_duplicate_wording_detected_for_standup_pair PASSED [ 81%]
tests/test_scc.py::test_check_raises_on_empty_corpus PASSED              [ 86%]
tests/test_scc.py::test_render_text_contains_every_status PASSED         [ 90%]
tests/test_scc.py::test_render_html_is_well_formed_and_has_no_em_dash PASSED [ 95%]
tests/test_scc.py::test_render_markdown_has_disposition_table PASSED     [100%]

============================= 22 passed in 0.25s ==============================
```

**Exit code: 0.** 22 passed, 0 failed, no network, no dependency on Ben's real skills dir (fixtures/skills only).

## 2. CLI on the bundled fixtures (fixtures/skills, 8 fake skills)

Command: `python -m scc check fixtures/skills`

```
Skill collision check
roots: fixtures/skills
skills scanned: 8   threshold: 0.30   near-dup ratio: 0.85

Disposition: 3 KEEP, 3 TUNE, 2 COLLISION

  COLLISION  note-taker                   collides with quick-capture (shared: 'capture an idea', capture, idea, later, quick, triage; jaccard 0.59)
  COLLISION  quick-capture                collides with note-taker (shared: 'capture an idea', capture, idea, later, quick, triage; jaccard 0.59)
  TUNE       daily-standup                narrow daily-standup's trigger; it is shadowed by standup-recap
  TUNE       set-reminder                 narrow set-reminder's trigger; it is shadowed by broad-reminder
  TUNE       standup-recap                when-to-use wording is 94% similar to daily-standup; add a disambiguating clause
  KEEP       broad-reminder               -
  KEEP       changelog-writer             -
  KEEP       deploy-checklist             -

Collision pairs (1)
  [collision] note-taker <-> quick-capture   jaccard-weighted score 0.59
      shared trigger phrases: 'capture an idea'
      shared keywords: capture, idea, later, quick, triage

Shadowed skills (2)
  [shadowed] set-reminder triggers are a strict subset of broad-reminder's
      suggestion: narrow set-reminder's trigger; it is shadowed by broad-reminder
  [shadowed] daily-standup triggers are a strict subset of standup-recap's
      suggestion: narrow daily-standup's trigger; it is shadowed by standup-recap

Near-duplicate when-to-use wording (1)
  daily-standup <-> standup-recap   text-similarity ratio 0.94
```

**Exit code: 0.**

**Planted findings confirmed:**
- The deliberate collision (`note-taker` / `quick-capture`, sharing the phrase `'capture an idea'`) is detected and shows the exact shared tokens.
- The deliberate shadow (`set-reminder` shadowed by `broad-reminder`) is detected with the exact suggested fix wording ("narrow set-reminder's trigger; it is shadowed by broad-reminder").
- Bonus: the algorithm independently found a second shadow pair (`daily-standup` shadowed by `standup-recap`, since the latter's description is a superset differing only by the word "whole") and a near-duplicate wording pair between the same two - neither was required by the plant, both are genuine detections.
- The two clean skills (`changelog-writer`, `deploy-checklist`) correctly land as KEEP.

This is also the committed sample report: `examples/sample-report.txt`, `examples/sample-report.md`, `examples/sample-report.html`.

## 3. Origin-story check: Ben's real `~/.claude/skills` corpus (read-only)

Command: `python -m scc check "/c/Users/Asus PC/.claude/skills"`

Reachable. Run was read-only - `check` only opens files for reading; no `--html`/`--md` output path pointed at the real skills directory, so nothing there was written or modified.

```
Skill collision check
roots: C:/Users/Asus PC/.claude/skills
skills scanned: 31   threshold: 0.30   near-dup ratio: 0.85

Disposition: 29 KEEP, 0 TUNE, 2 COLLISION

  COLLISION  sync-plugins                 collides with sync-skills (shared: add, additional, alone, already, authoritative, between, +26 more; jaccard 0.74)
  COLLISION  sync-skills                  collides with sync-plugins (shared: add, additional, alone, already, authoritative, between, +26 more; jaccard 0.74)
  KEEP       build-apps                   -
  KEEP       checkpoint-memories          -
  KEEP       compact-memory-index         -
  KEEP       first-run-review             -
  KEEP       generate-guide               -
  KEEP       generate-ideas               -
  KEEP       generate-ideas-k             -
  KEEP       job-fit-research             -
  KEEP       judgment-run                 -
  KEEP       linear-dupe-check            -
  KEEP       linear-file-bugs             -
  KEEP       linear-open-issues           -
  KEEP       linear-qa-intake             -
  KEEP       linear-sync-cache            -
  KEEP       memory-audit                 -
  KEEP       new-project                  -
  KEEP       portfolio-scout              -
  KEEP       portfolio-ship               -
  KEEP       pretty-guide                 -
  KEEP       red-neo                      -
  KEEP       regents-orchestrator         -
  KEEP       research-game-franchise      -
  KEEP       session-end                  -
  KEEP       session-start                -
  KEEP       skill-audit                  -
  KEEP       skill-authoring-standard     -
  KEEP       sync-memories                -
  KEEP       test-webapp                  -
  KEEP       upgrade-app                  -

Collision pairs (1)
  [collision] sync-plugins <-> sync-skills   jaccard-weighted score 0.74
      shared keywords: add, additional, alone, already, authoritative, between, claude, code, curated, dry, folder, left, local, locations, machine, nas, new, newest, only, peers, plugin, present, project, registered, repo, repos, sources, sync, synced, txt, whitelist, wins

Shadowed skills (0)
  none found

Near-duplicate when-to-use wording (0)
  none found
```

**Exit code: 0.**

**Real finding:** `sync-plugins` and `sync-skills` share 32 keywords (jaccard 0.74) - the two skills are near-mirror templates (one manages plugins, the other manages skills; the description wording barely changed between them). This is a genuine, defensible collision: both skills describe syncing curated Claude Code assets between local machine, NAS, and registered project repos, with "NAS is the authoritative whitelist" language repeated near-verbatim. No shadowed pairs and no near-duplicate wording pairs among the real 31 skills.

## Honesty notes

- 31 real skills scanned, not a round number picked to sound good - that is the actual count in `~/.claude/skills` at build time (2026-07-04).
- The tool never wrote to any file under `~/.claude/skills`. Verified: no `--html`/`--md` flags were passed pointing at that directory in any run above; `check()` only opens `SKILL.md` files with mode `"r"` (see `scc/discovery.py`).
- No em-dash sweep: `grep` for `—` across the repo finds it only in the PRD title (matching the same house convention as `claude-context-audit`'s and `mcp-schema-lint`'s own PRD.md titles) and one test assertion string (`assert "—" not in out`) - neither is user-facing product copy.
