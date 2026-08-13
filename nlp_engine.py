import spacy
from spacy.matcher import PhraseMatcher
from skills_taxonomy import get_all_skill_variants

_nlp = None
_matcher = None
_variant_map = None

def _load():
    global _nlp, _matcher, _variant_map
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        _variant_map = get_all_skill_variants()
        _matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
        patterns = [_nlp.make_doc(text) for text in _variant_map.keys()]
        _matcher.add("SKILLS", patterns)
    return _nlp, _matcher, _variant_map

def extract_skills_nlp(text):
    """
    Extracts canonical skills from text using phrase matching.
    Returns a set of canonical skill names (e.g. "javascript" even if text said "JS").
    """
    if not text or not text.strip():
        return set()
    nlp, matcher, variant_map = _load()
    doc = nlp(text.lower())
    matches = matcher(doc)
    found = set()
    for match_id, start, end in matches:
        span_text = doc[start:end].text.lower()
        canonical = variant_map.get(span_text)
        if canonical:
            found.add(canonical)
    return found


if __name__ == "__main__":
    resume = "Experienced in ML, JS, and cloud computing. Worked with Node.js and MongoDB. Strong communication skills."
    jd = "Looking for a candidate skilled in Machine Learning, JavaScript, AWS, and databases like MongoDB. Good teamwork required."

    r_skills = extract_skills_nlp(resume)
    j_skills = extract_skills_nlp(jd)
    print("Resume skills:", r_skills)
    print("JD skills:", j_skills)
    print("Matched:", r_skills & j_skills)
    print("Missing:", j_skills - r_skills)
