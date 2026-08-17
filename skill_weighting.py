"""
RESUFIT — Skill Weighting

Detects whether a skill mentioned in a job description is REQUIRED
(must-have) or PREFERRED (nice-to-have), by looking at the language
used in the sentence the skill appears in.

Required skills count more heavily toward the match score than
preferred ones — matching how real hiring managers actually weigh
job requirements.
"""

import spacy
from spacy.matcher import PhraseMatcher
from skills_taxonomy import get_all_skill_variants

REQUIRED_MARKERS = [
    "required", "must have", "must-have", "mandatory", "essential",
    "need to have", "should have", "minimum qualification", "prerequisite",
]

PREFERRED_MARKERS = [
    "preferred", "nice to have", "nice-to-have", "plus", "bonus",
    "good to have", "advantageous", "a plus", "desirable", "optional",
]

REQUIRED_WEIGHT = 2
PREFERRED_WEIGHT = 1

_nlp = None
_matcher = None
_variant_map = None


def _load():
    global _nlp, _matcher, _variant_map
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner"])
        _variant_map = get_all_skill_variants()
        _matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
        patterns = [_nlp.make_doc(text) for text in _variant_map.keys()]
        _matcher.add("SKILLS", patterns)
    return _nlp, _matcher, _variant_map


def _classify_sentence(sent_text):
    """Returns 'required', 'preferred', or 'unspecified' based on language cues."""
    lower = sent_text.lower()
    if any(marker in lower for marker in PREFERRED_MARKERS):
        return "preferred"
    if any(marker in lower for marker in REQUIRED_MARKERS):
        return "required"
    return "unspecified"


def extract_weighted_skills(text):
    """
    Extracts skills from job description text along with their weight category.

    Returns a dict: { canonical_skill: {"category": "required"|"preferred"|"unspecified", "weight": int} }

    Skills with no explicit language cue default to "required" — most job
    descriptions list core skills plainly without qualifying language, and
    treating unmarked skills as core requirements is the safer assumption.
    """
    if not text or not text.strip():
        return {}

    nlp, matcher, variant_map = _load()
    doc = nlp(text)
    matches = matcher(doc)

    skill_to_sentences = {}
    for match_id, start, end in matches:
        span = doc[start:end]
        canonical = variant_map.get(span.text.lower())
        if not canonical:
            continue
        sent = span.sent
        skill_to_sentences.setdefault(canonical, []).append(sent.text)

    weighted = {}
    for skill, sentences in skill_to_sentences.items():
        categories = [_classify_sentence(s) for s in sentences]
        if "preferred" in categories and "required" not in categories:
            category = "preferred"
        else:
            # required, unspecified, or mixed -> treat as required (safer default)
            category = "required" if "required" in categories else "unspecified"

        weight = PREFERRED_WEIGHT if category == "preferred" else REQUIRED_WEIGHT
        weighted[skill] = {"category": category, "weight": weight}

    return weighted


if __name__ == "__main__":
    jd = """
    We are looking for a Data Analyst. Python and SQL are required.
    Experience with Power BI is a plus. Machine learning knowledge is preferred.
    Strong communication skills are essential for this role.
    """
    result = extract_weighted_skills(jd)
    for skill, info in result.items():
        print(f"{skill}: {info['category']} (weight={info['weight']})")
