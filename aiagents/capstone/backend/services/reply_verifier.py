import re

MIN_QUOTE_CHARS = 12

# Characters models like to swap for look-alikes, and markdown noise.
_REPLACEMENTS = {
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
    " ": " ", " ": " ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "*": "", "`": "", "|": " ",
}

# The pipeline never opens tickets, sends emails or hands anything to a person
# while it drafts a reply, so a draft saying it already did is always unsupported.
_COMPLETED_ACTION = re.compile(
    r"\b(?:i|we)(?:['’]ve| have)\s+"
    r"(?:\w+\s+)?"
    r"(?:handed|passed|escalated|forwarded|opened|created|raised|sent|emailed|notified|assigned|logged|filed)\b"
    r"|\b(?:has|have) been\s+(?:handed|passed|escalated|forwarded|opened|created|raised|sent|emailed|notified|assigned|logged|filed)\b",
    re.IGNORECASE,
)

_NUMBER_TOKEN = re.compile(r"[\w$.\-]*\d[\w.\-]*")


_LIST_MARKER = re.compile(r"(?m)^[ 	]*(?:[-•]|#{1,6}|\d+\.)[ 	]+")
_WORD = re.compile(r"[a-z0-9]+")

# a quote counts as supported when at least this share of its words exist in
# the findings; models often stitch two lines together instead of copying one
MIN_WORD_COVERAGE = 0.85


def normalize(text):
    for old, new in _REPLACEMENTS.items():
        text = text.replace(old, new)
    text = _LIST_MARKER.sub("", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _quote_supported(quote, findings_norm, findings_words):
    if quote in findings_norm:
        return True

    words = [word for word in _WORD.findall(quote) if len(word) >= 3]
    if len(words) < 3:
        return False

    found = sum(word in findings_words for word in words)
    return found / len(words) >= MIN_WORD_COVERAGE


def verify_claims(claims, findings):
    """Return a list of problems. An empty list means every claim checked out.

    This verifies that the quoted support really exists in the findings and
    that every number, date or id in the claim appears in the findings. It
    cannot verify that a real quote actually supports the claim, which is why
    the LLM's own judgement is still part of the evaluation.
    """
    findings_norm = normalize(findings)
    findings_words = set(_WORD.findall(findings_norm))
    problems = []

    for claim in claims:
        statement = claim.statement
        quote = normalize(claim.supporting_quote or "")

        if not quote:
            problems.append(f"No supporting evidence for: {statement}")
            continue

        if len(quote) < MIN_QUOTE_CHARS:
            problems.append(f"Supporting quote is too short to count as evidence for: {statement}")
            continue

        if not _quote_supported(quote, findings_norm, findings_words):
            problems.append(f"The quoted evidence does not appear in the findings for: {statement}")
            continue

        for token in _NUMBER_TOKEN.findall(normalize(statement)):
            token = token.strip(".,-")
            if token and token not in findings_norm:
                problems.append(f"'{token}' does not appear anywhere in the findings, in: {statement}")
                break

    return problems


def find_completed_action_claims(draft):
    return [
        f"The reply says an action was already done ('{match.group(0)}'), but nothing has been done yet"
        for match in _COMPLETED_ACTION.finditer(draft)
    ]


CANNED_CLARIFY = "Hi! I can help with billing, your account, or technical problems. What's going on?"

_LINK = re.compile(r"https?://|www\.", re.IGNORECASE)

# anything that looks like a number, amount or id
_NUMBERISH = re.compile(r"[\w$.,]*[\d$][\w$.,]*")

# Nothing is handed to a person on this path, so the reply must not suggest it.
_IMPLIES_A_PERSON = re.compile(
    r"\b(team|human|specialist|staff|colleague|someone|review|follow up|get back to you|escalat\w*)\b",
    re.IGNORECASE,
)

_THANKS = re.compile(r"\b(thanks|thank you|thx|cheers|appreciate)\b", re.IGNORECASE)


def clean_clarify_reply(text, customer_message=""):
    """The router writes the reply to a greeting or a vague message. Small talk
    has no evidence to check, so it must contain no facts and no promises: no
    numbers, amounts or links, no claim that something was done, and no hint
    that a person will look at it, because nobody will. It must ask a question
    unless the customer only said thanks. Anything else is replaced with a
    fixed friendly message.
    """
    text = (text or "").strip()

    if not text or len(text) > 400:
        return CANNED_CLARIFY
    if _LINK.search(text) or find_completed_action_claims(text):
        return CANNED_CLARIFY

    # a number is fine when the customer wrote it, because the reply is only
    # repeating it back. A number the customer did not write would be a made up fact.
    for token in _NUMBERISH.findall(text):
        token = token.strip(".,")
        if token and token not in (customer_message or ""):
            return CANNED_CLARIFY
    if _IMPLIES_A_PERSON.search(text):
        return CANNED_CLARIFY
    if "?" not in text and not _THANKS.search(customer_message or ""):
        return CANNED_CLARIFY

    return text


def mentions_a_person(text):
    """True when a reply tells the customer that a person will look at their ticket."""
    return bool(_IMPLIES_A_PERSON.search(text or ""))
