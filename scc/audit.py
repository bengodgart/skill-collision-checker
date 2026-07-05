"""Aggregate discovery + signal extraction + pairwise analysis into a Report
with one KEEP / TUNE / COLLISION disposition per skill.

Precedence when a skill shows up in more than one finding: shadow > collision
> near-duplicate > keep. Shadow and collision both get a TUNE/COLLISION
disposition with a specific, ready-to-use suggestion; near-duplicate wording
that is not also a collision is a softer TUNE. A clean skill with none of the
above is KEEP.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .discovery import Corpus, discover
from .collisions import (
    CollisionPair, ShadowPair, NearDupPair, ScoredSkill,
    score_skills, find_shadows, find_collisions, find_near_duplicates,
    DEFAULT_THRESHOLD, DEFAULT_NEAR_RATIO,
)

KEEP = "KEEP"
TUNE = "TUNE"
COLLISION = "COLLISION"


@dataclass
class Disposition:
    skill: str
    status: str
    detail: str


@dataclass
class Report:
    corpus: Corpus
    scored: list[ScoredSkill]
    shadows: list[ShadowPair]
    collisions: list[CollisionPair]
    near_dups: list[NearDupPair]
    dispositions: list[Disposition] = field(default_factory=list)
    threshold: float = DEFAULT_THRESHOLD
    near_ratio: float = DEFAULT_NEAR_RATIO

    @property
    def skill_count(self) -> int:
        return len(self.scored)

    @property
    def counts(self) -> dict[str, int]:
        c = {KEEP: 0, TUNE: 0, COLLISION: 0}
        for d in self.dispositions:
            c[d.status] += 1
        return c


def _format_tokens(phrases: list[str], keywords: list[str], limit: int = 6) -> str:
    tokens = [f"'{p}'" for p in phrases] + list(keywords)
    shown = tokens[:limit]
    text = ", ".join(shown)
    if len(tokens) > limit:
        text += f", +{len(tokens) - limit} more"
    return text


def _build_dispositions(scored: list[ScoredSkill], shadows: list[ShadowPair],
                         collisions: list[CollisionPair], near_dups: list[NearDupPair]) -> list[Disposition]:
    shadow_by_narrower = {s.narrower: s for s in shadows}
    collisions_by_skill: dict[str, list[CollisionPair]] = {}
    for pair in collisions:
        collisions_by_skill.setdefault(pair.a, []).append(pair)
        collisions_by_skill.setdefault(pair.b, []).append(pair)
    near_dup_by_skill: dict[str, list[NearDupPair]] = {}
    for pair in near_dups:
        near_dup_by_skill.setdefault(pair.a, []).append(pair)
        near_dup_by_skill.setdefault(pair.b, []).append(pair)

    dispositions: list[Disposition] = []
    for item in scored:
        label = item.skill.label

        shadow = shadow_by_narrower.get(label)
        if shadow is not None:
            dispositions.append(Disposition(
                skill=label, status=TUNE,
                detail=f"narrow {label}'s trigger; it is shadowed by {shadow.broader}",
            ))
            continue

        own_collisions = collisions_by_skill.get(label)
        if own_collisions:
            parts = []
            for pair in own_collisions:
                other = pair.b if pair.a == label else pair.a
                tokens = _format_tokens(pair.shared_phrases, pair.shared_keywords)
                parts.append(f"collides with {other} (shared: {tokens}; score {pair.score:.2f})")
            dispositions.append(Disposition(skill=label, status=COLLISION, detail="; ".join(parts)))
            continue

        own_near_dups = near_dup_by_skill.get(label)
        if own_near_dups:
            other = own_near_dups[0].b if own_near_dups[0].a == label else own_near_dups[0].a
            ratio = own_near_dups[0].ratio
            dispositions.append(Disposition(
                skill=label, status=TUNE,
                detail=f"when-to-use wording is {ratio:.0%} similar to {other}; add a disambiguating clause",
            ))
            continue

        dispositions.append(Disposition(skill=label, status=KEEP, detail="-"))

    return dispositions


def check(roots: list[str], threshold: float = DEFAULT_THRESHOLD,
          near_ratio: float = DEFAULT_NEAR_RATIO) -> Report:
    corpus = discover(roots)
    if not corpus.skills:
        raise ValueError(f"no SKILL.md files found under: {', '.join(roots)}")

    scored = score_skills(corpus.skills)
    shadows = find_shadows(scored)
    shadowed_pairs = {frozenset((s.narrower, s.broader)) for s in shadows}
    collisions = find_collisions(scored, threshold=threshold, shadowed_pairs=shadowed_pairs)
    near_dups = find_near_duplicates(scored, near_ratio=near_ratio)
    dispositions = _build_dispositions(scored, shadows, collisions, near_dups)

    return Report(
        corpus=corpus, scored=scored, shadows=shadows, collisions=collisions,
        near_dups=near_dups, dispositions=dispositions,
        threshold=threshold, near_ratio=near_ratio,
    )
