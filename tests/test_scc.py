"""Tests for skill-collision-checker. pytest, no network, no dependency on
Ben's real ~/.claude/skills - everything runs against fixtures/skills.

Run: python -m pytest tests/ -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scc.discovery import parse_frontmatter, discover
from scc.signals import extract_signals
from scc.collisions import collision_score, find_shadows, find_collisions, find_near_duplicates, score_skills
from scc.audit import check, KEEP, TUNE, COLLISION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "fixtures", "skills")


# --- frontmatter parsing -----------------------------------------------

def test_parse_frontmatter_quoted_value():
    text = '---\nname: foo\ndescription: "Do the thing: really."\n---\nbody\n'
    fields = parse_frontmatter(text)
    assert fields["name"] == "foo"
    assert fields["description"] == "Do the thing: really."


def test_parse_frontmatter_unquoted_value():
    text = "---\nname: bar\ndescription: Plain text, no quotes.\n---\nbody\n"
    fields = parse_frontmatter(text)
    assert fields["description"] == "Plain text, no quotes."


def test_parse_frontmatter_no_block_returns_empty():
    assert parse_frontmatter("# just a heading\nno frontmatter here") == {}


# --- discovery -----------------------------------------------------------

def test_discover_finds_all_fixture_skills():
    corpus = discover([FIXTURES])
    names = {s.name for s in corpus.skills}
    assert names == {
        "note-taker", "quick-capture", "broad-reminder", "set-reminder",
        "daily-standup", "standup-recap", "changelog-writer", "deploy-checklist",
    }


def test_discover_missing_root_is_skipped_not_fatal():
    corpus = discover([FIXTURES, os.path.join(FIXTURES, "does-not-exist")])
    assert len(corpus.skipped) == 1
    assert len(corpus.skills) == 8


# --- signal extraction -----------------------------------------------------

def test_extract_signals_quoted_phrases():
    sig = extract_signals("Use when the user says 'take a note' or 'jot this down'.")
    assert "take a note" in sig.phrases
    assert "jot this down" in sig.phrases


def test_extract_signals_keywords_drop_stopwords():
    sig = extract_signals("Use when the user says 'do it' for the team.")
    assert "the" not in sig.keywords
    assert "when" not in sig.keywords
    assert "team" in sig.keywords


def test_extract_signals_no_quotes_still_gets_keywords():
    sig = extract_signals("Write a changelog entry grouped by feature, fix, and chore.")
    assert sig.phrases == set()
    assert "changelog" in sig.keywords


# --- collision scoring -----------------------------------------------------

def test_collision_score_shared_phrase_dominates():
    a = extract_signals("Use when the user says 'capture an idea'.")
    b = extract_signals("Use when the user says 'capture an idea' for later.")
    score, shared_phrases, _ = collision_score(a, b)
    assert "capture an idea" in shared_phrases
    assert score >= 0.3


def test_collision_score_disjoint_is_zero():
    a = extract_signals("Summarize a changelog from commits.")
    b = extract_signals("Walk through a pre-deploy checklist for migrations.")
    score, shared_phrases, shared_keywords = collision_score(a, b)
    assert shared_phrases == set()
    assert score < 0.3


# --- full fixture corpus: the planted findings must be detected ----------

def test_planted_collision_note_taker_quick_capture():
    result = check([FIXTURES])
    pairs = {frozenset((p.a, p.b)) for p in result.collisions}
    assert frozenset(("note-taker", "quick-capture")) in pairs
    pair = next(p for p in result.collisions if {p.a, p.b} == {"note-taker", "quick-capture"})
    assert "capture an idea" in pair.shared_phrases


def test_planted_shadow_set_reminder_by_broad_reminder():
    result = check([FIXTURES])
    shadow = next((s for s in result.shadows if s.narrower == "set-reminder"), None)
    assert shadow is not None
    assert shadow.broader == "broad-reminder"


def test_shadowed_pair_not_also_double_counted_as_collision():
    result = check([FIXTURES])
    collision_pairs = {frozenset((p.a, p.b)) for p in result.collisions}
    assert frozenset(("set-reminder", "broad-reminder")) not in collision_pairs


def test_disposition_table_covers_every_skill_exactly_once():
    result = check([FIXTURES])
    labels = [d.skill for d in result.dispositions]
    assert len(labels) == 8
    assert len(set(labels)) == 8


def test_set_reminder_disposition_is_tune_with_suggestion():
    result = check([FIXTURES])
    d = next(d for d in result.dispositions if d.skill == "set-reminder")
    assert d.status == TUNE
    assert "shadowed by broad-reminder" in d.detail


def test_note_taker_disposition_is_collision_with_shared_tokens():
    result = check([FIXTURES])
    d = next(d for d in result.dispositions if d.skill == "note-taker")
    assert d.status == COLLISION
    assert "capture an idea" in d.detail


def test_clean_skills_are_kept():
    result = check([FIXTURES])
    by_name = {d.skill: d for d in result.dispositions}
    assert by_name["changelog-writer"].status == KEEP
    assert by_name["deploy-checklist"].status == KEEP


def test_near_duplicate_wording_detected_for_standup_pair():
    result = check([FIXTURES])
    pairs = {frozenset((d.a, d.b)) for d in result.near_dups}
    assert frozenset(("daily-standup", "standup-recap")) in pairs


def test_check_raises_on_empty_corpus(tmp_path):
    empty = tmp_path / "empty_skills"
    empty.mkdir()
    try:
        check([str(empty)])
        assert False, "expected ValueError on an empty corpus"
    except ValueError:
        pass


# --- report rendering (smoke) ---------------------------------------------

def test_render_text_contains_every_status():
    from scc.report import render_text
    result = check([FIXTURES])
    text = render_text(result)
    assert "COLLISION" in text
    assert "TUNE" in text
    assert "KEEP" in text
    assert "capture an idea" in text


def test_render_html_is_well_formed_and_has_no_em_dash():
    from scc.report import render_html
    result = check([FIXTURES])
    out = render_html(result)
    assert out.startswith("<!DOCTYPE html>")
    assert out.rstrip().endswith("</html>")
    assert "—" not in out


def test_render_markdown_has_disposition_table():
    from scc.report import render_markdown
    result = check([FIXTURES])
    md = render_markdown(result)
    assert "| Status | Skill | Detail |" in md
