"""Pairwise analysis: collisions, shadowed skills, near-duplicate wording.

Three independent checks over every skill pair (A, B):

1. Shadow: B's full trigger surface (phrases + keywords) is a non-empty
   strict subset of A's. B never fires when A would not also fire - B is
   redundant next to A. Reported once, from the narrower skill's side.

2. Collision: shared trigger phrases and/or a keyword Jaccard at or above
   `threshold`. Two skills genuinely fighting over the same words. A pair
   already classified as a shadow is not also reported as a collision - the
   shadow finding is the more specific, more actionable one.

3. Near-duplicate wording: the two full descriptions are textually similar
   (difflib ratio at or above `near_ratio`), independent of 1 and 2. Two
   authors wrote almost the same "when to use" sentence for different skills.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import combinations

from .discovery import Skill
from .signals import Signals, extract_signals

DEFAULT_THRESHOLD = 0.3
DEFAULT_NEAR_RATIO = 0.85
PHRASE_WEIGHT = 0.34   # each exact shared trigger phrase is a strong signal on its own


@dataclass
class ScoredSkill:
    skill: Skill
    signals: Signals


@dataclass
class CollisionPair:
    a: str
    b: str
    score: float
    shared_phrases: list[str]
    shared_keywords: list[str]


@dataclass
class ShadowPair:
    narrower: str
    broader: str


@dataclass
class NearDupPair:
    a: str
    b: str
    ratio: float


def score_skills(skills: list[Skill]) -> list[ScoredSkill]:
    return [ScoredSkill(skill=s, signals=extract_signals(s.description)) for s in skills]


def collision_score(a: Signals, b: Signals) -> tuple[float, set[str], set[str]]:
    shared_phrases = a.phrases & b.phrases
    shared_keywords = a.keywords & b.keywords
    union_keywords = a.keywords | b.keywords
    jaccard = len(shared_keywords) / len(union_keywords) if union_keywords else 0.0
    phrase_bonus = min(len(shared_phrases) * PHRASE_WEIGHT, 1.0)
    score = min(1.0, jaccard + phrase_bonus)
    return score, shared_phrases, shared_keywords


def _is_strict_subset(smaller: set[str], larger: set[str]) -> bool:
    if not smaller:
        return False
    return smaller < larger  # proper subset: every element in larger too, and larger has more


def find_shadows(scored: list[ScoredSkill]) -> list[ShadowPair]:
    shadows: list[ShadowPair] = []
    for x, y in combinations(scored, 2):
        x_tokens, y_tokens = x.signals.trigger_tokens, y.signals.trigger_tokens
        if _is_strict_subset(x_tokens, y_tokens):
            shadows.append(ShadowPair(narrower=x.skill.label, broader=y.skill.label))
        elif _is_strict_subset(y_tokens, x_tokens):
            shadows.append(ShadowPair(narrower=y.skill.label, broader=x.skill.label))
    return shadows


def find_collisions(scored: list[ScoredSkill], threshold: float = DEFAULT_THRESHOLD,
                     shadowed_pairs: set[frozenset[str]] | None = None) -> list[CollisionPair]:
    shadowed_pairs = shadowed_pairs or set()
    pairs: list[CollisionPair] = []
    for x, y in combinations(scored, 2):
        key = frozenset((x.skill.label, y.skill.label))
        if key in shadowed_pairs:
            continue
        score, shared_phrases, shared_keywords = collision_score(x.signals, y.signals)
        if score >= threshold:
            pairs.append(CollisionPair(
                a=x.skill.label, b=y.skill.label, score=score,
                shared_phrases=sorted(shared_phrases),
                shared_keywords=sorted(shared_keywords),
            ))
    pairs.sort(key=lambda p: p.score, reverse=True)
    return pairs


def find_near_duplicates(scored: list[ScoredSkill], near_ratio: float = DEFAULT_NEAR_RATIO) -> list[NearDupPair]:
    dups: list[NearDupPair] = []
    for x, y in combinations(scored, 2):
        if not x.signals.normalized_text or not y.signals.normalized_text:
            continue
        ratio = SequenceMatcher(None, x.signals.normalized_text, y.signals.normalized_text).ratio()
        if ratio >= near_ratio:
            dups.append(NearDupPair(a=x.skill.label, b=y.skill.label, ratio=ratio))
    dups.sort(key=lambda d: d.ratio, reverse=True)
    return dups
