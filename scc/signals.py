"""Extract trigger signals from a skill's description.

Three things come out of one description string:
- trigger phrases: the exact quoted strings the author wrote as trigger
  examples ('take a note', '/note-taker --urgent'). These are the strongest
  signal - if two skills quote the same phrase, they are fighting over the
  same words verbatim.
- keywords: the salient content words in the description, normalized and
  stopword-filtered, used for a Jaccard overlap when there is no exact quoted
  match.
- normalized_text: the whole description, lowercased and punctuation-stripped,
  used to catch near-duplicate "when to use" wording via a text-similarity
  ratio rather than a token set.

Deterministic, no embeddings: quoted-phrase equality plus a keyword Jaccard,
per the brief.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

QUOTE_RE = re.compile(r"'([^']{2,80})'|\"([^\"]{2,80})\"")
WORD_RE = re.compile(r"[a-z0-9]+")
PUNCT_RE = re.compile(r"[^a-z0-9\s]")
WS_RE = re.compile(r"\s+")

# Function words and skill-boilerplate that would otherwise inflate every
# pair's overlap regardless of actual subject matter.
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "at", "by", "for",
    "with", "without", "into", "onto", "from", "as", "is", "are", "was",
    "were", "be", "been", "being", "it", "its", "this", "that", "these",
    "those", "you", "your", "yours", "user", "users", "me", "my", "i", "we",
    "our", "he", "she", "they", "them", "their", "not", "no", "so", "than",
    "then", "when", "while", "if", "any", "all", "some", "one", "two",
    "three", "or", "e", "g", "eg", "etc", "use", "used", "using", "uses",
    "says", "say", "said", "examples", "example", "run", "runs",
}

MIN_KEYWORD_LEN = 3


@dataclass
class Signals:
    phrases: set[str] = field(default_factory=set)          # normalized quoted phrases
    phrases_display: list[str] = field(default_factory=list)  # original-case, de-duped, ordered
    keywords: set[str] = field(default_factory=set)
    normalized_text: str = ""

    @property
    def trigger_tokens(self) -> set[str]:
        """Phrases and keywords combined - the full trigger surface used for
        the shadow (subset) check."""
        return self.phrases | self.keywords


def _normalize_phrase(phrase: str) -> str:
    phrase = phrase.strip()
    phrase = PUNCT_RE.sub(" ", phrase.lower())
    phrase = WS_RE.sub(" ", phrase).strip()
    return phrase


def _normalize_text(text: str) -> str:
    text = PUNCT_RE.sub(" ", text.lower())
    text = WS_RE.sub(" ", text).strip()
    return text


def extract_signals(description: str) -> Signals:
    if not description:
        return Signals()

    phrases: set[str] = set()
    phrases_display: list[str] = []
    for match in QUOTE_RE.finditer(description):
        raw = match.group(1) if match.group(1) is not None else match.group(2)
        raw = raw.strip()
        if raw.startswith("/"):
            # a slash-command invocation example (e.g. '/set-reminder --flag'),
            # not a natural-language trigger phrase. Its words already feed
            # `keywords` via the full-text tokenization below; skipping it
            # here keeps a skill's own command name from becoming a "trigger
            # phrase" that could never be a subset of a broader skill's set.
            continue
        norm = _normalize_phrase(raw)
        if not norm or norm in phrases:
            continue
        phrases.add(norm)
        phrases_display.append(raw)

    words = WORD_RE.findall(description.lower())
    keywords = {
        w for w in words
        if len(w) >= MIN_KEYWORD_LEN and w not in STOPWORDS and not w.isdigit()
    }

    return Signals(
        phrases=phrases,
        phrases_display=phrases_display,
        keywords=keywords,
        normalized_text=_normalize_text(description),
    )
