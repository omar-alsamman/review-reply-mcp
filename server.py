"""Local-business review reply — a narrow, single-purpose MCP server.

One job: draft a professional, paste-ready reply to a Google / local-business
review. No network calls, no API keys, no paid services. Pure Python,
template + keyword heuristics, works fully offline over stdio.

Tools:
  - draft_review_reply: draft a reply (<=600 chars) + escalation flag +
    suggested follow-up + what-not-to-say guidance.
  - classify_review: band / sentiment / topics / escalation for triage.

Safety rules baked into every draft:
  - Never invents facts: no fake staff names, discounts, refunds or promises.
  - Never admits legal fault; never blames the reviewer; never argues.
  - 1-2 star reviews always flag for human follow-up and invite the
    reviewer to contact the business directly (no contact details invented).

Run:  python server.py        (stdio transport, for Claude Desktop / Smithery)
Test: python test_review_reply.py
"""

import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="review-reply",
    instructions=(
        "Draft professional replies to local-business reviews. "
        "Call draft_review_reply with the review text, star rating (1-5), "
        "business name and business type; it returns a paste-ready reply "
        "under 600 characters plus escalation and follow-up guidance. "
        "Use classify_review first when triaging many reviews. "
        "Never publish a reply without a human reading it first, "
        "especially for 1-2 star reviews."
    ),
)

MAX_REVIEW_CHARS = 2000
MAX_DRAFT_CHARS = 600

# topic -> (keywords, short label used in the draft)
TOPICS = {
    "wait_time": (
        ["wait", "waiting", "waited", "slow", "took forever", "took ages",
         "late", "delay", "hour", "minutes"],
        "the wait",
    ),
    "staff_service": (
        ["rude", "staff", "friendly", "helpful", "service", "waiter",
         "waitress", "employee", "manager", "welcoming", "polite"],
        "the service",
    ),
    "food_quality": (
        ["food", "delicious", "tasty", "cold food", "stale", "fresh",
         "menu", "dish", "meal", "coffee", "pizza", "burger"],
        "the food",
    ),
    "price": (
        ["price", "expensive", "overcharged", "charged", "cost", "pricey",
         "cheap", "value", "bill", "overcharge"],
        "the pricing",
    ),
    "cleanliness": (
        ["clean", "dirty", "filthy", "messy", "spotless", "hygiene"],
        "the cleanliness",
    ),
    "atmosphere": (
        ["atmosphere", "ambience", "cozy", "noisy", "loud", "comfortable",
         "place", "vibe"],
        "the atmosphere",
    ),
    "quality_of_work": (
        ["quality", "work", "repair", "fixed", "install", "job done",
         "craftsmanship"],
        "the quality of the work",
    ),
    "communication": (
        ["called", "never called", "no response", "ignored", "responsive",
         "answered", "communication", "ghosted"],
        "the communication",
    ),
    "appointment_booking": (
        ["appointment", "booking", "scheduled", "rescheduled", "booked"],
        "the booking",
    ),
    "delivery": (
        ["delivery", "delivered", "arrived late", "order arrived"],
        "the delivery",
    ),
}

POSITIVE_WORDS = [
    "great", "excellent", "amazing", "wonderful", "fantastic", "love",
    "loved", "best", "friendly", "helpful", "delicious", "perfect",
    "highly recommend", "recommend", "beautiful", "quick", "professional",
    "clean", "fresh", "happy", "pleased", "impressed", "thank",
]
NEGATIVE_WORDS = [
    "terrible", "awful", "horrible", "rude", "worst", "disappointed",
    "disappointing", "bad", "poor", "dirty", "slow", "overcharged",
    "expensive", "never again", "avoid", "waste", "angry", "frustrated",
    "unprofessional", "ignored", "broken", "wrong",
]
ESCALATION_WORDS = [
    "food poisoning", "sick", "scam", "fraud", "stole", "stolen",
    "discrimination", "racist", "injured", "hurt", "health code",
    "lawsuit", "lawyer", "police", "threatened",
]


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _detect_topics(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for topic, (keywords, _label) in TOPICS.items():
        if any(k in lowered for k in keywords):
            found.append(topic)
    return found


def _specific_detail(text: str, topics: list[str]) -> str:
    """Shortest sentence mentioning a detected topic, capped at 120 chars.

    Used so the draft references what the reviewer actually said, instead
    of a generic 'thanks for your feedback'.
    """
    if not topics:
        return ""
    keywords = [k for t in topics for k in TOPICS[t][0]]
    best = ""
    for sentence in _sentences(text):
        low = sentence.lower()
        if any(k in low for k in keywords):
            if not best or len(sentence) < len(best):
                best = sentence
    if len(best) > 120:
        best = best[:117].rstrip() + "..."
    return best


def _topic_label(topics: list[str]) -> str:
    if not topics:
        return "your experience"
    return TOPICS[topics[0]][1]


def _validate(rating: int, review_text: str, business_name: str) -> None:
    if not isinstance(rating, int) or isinstance(rating, bool):
        raise ValueError("rating must be an integer 1-5")
    if rating < 1 or rating > 5:
        raise ValueError("rating must be between 1 and 5")
    if not review_text or not review_text.strip():
        raise ValueError("review_text must not be empty")
    if len(review_text) > MAX_REVIEW_CHARS:
        raise ValueError(f"review_text must be under {MAX_REVIEW_CHARS} characters")
    if not business_name or not business_name.strip():
        raise ValueError("business_name must not be empty")


def _greeting(reviewer_name: str, tone: str) -> str:
    name = (reviewer_name or "").strip()
    if name:
        return f"Thank you, {name}!"
    if tone == "professional":
        return "Thank you for your review."
    return "Thank you so much!"


def _signoff(business_name: str) -> str:
    return f"— The team at {business_name.strip()}"


def _enforce_length(draft: str) -> str:
    if len(draft) <= MAX_DRAFT_CHARS:
        return draft
    # Trim the middle sentence rather than cutting the sign-off.
    trimmed = draft[: MAX_DRAFT_CHARS - 3].rsplit(" ", 1)[0] + "..."
    return trimmed


def build_draft(
    review_text: str,
    rating: int,
    business_name: str,
    business_type: str = "",
    tone: str = "warm",
    reviewer_name: str = "",
) -> dict:
    """Pure draft logic (no MCP) so it can be unit-tested directly."""
    tone = (tone or "warm").lower()
    if tone not in ("warm", "professional", "apologetic"):
        tone = "warm"
    _validate(rating, review_text, business_name)
    biz = business_name.strip()
    topics = _detect_topics(review_text)
    detail = _specific_detail(review_text, topics)
    label = _topic_label(topics)
    greet = _greeting(reviewer_name, tone)
    if rating <= 2:
        # A chirpy "Thank you so much!" before an apology reads as tone-deaf.
        name = (reviewer_name or "").strip()
        greet = (
            f"Thank you, {name}, for bringing this to our attention."
            if name
            else "Thank you for bringing this to our attention."
        )
    signoff = _signoff(biz)

    if rating >= 5:
        praise = f"We're delighted {label} stood out"
        if detail:
            praise = f"We're delighted to hear it — {detail.rstrip('.!')}"
        body = (
            f"{greet} {praise}. "
            f"Thank you for choosing {biz}, and we hope to "
            f"welcome you back soon!"
        )
        draft = f"{body} {signoff}"
        follow_up = "None — thank the reviewer; no follow-up needed."
        escalation = False
    elif rating == 4:
        body = (
            f"{greet} We're glad {label} worked well for you, and we "
            f"appreciate you taking the time to share it. "
            f"We'll keep working to earn that fifth star — "
            f"hope to see you again soon!"
        )
        draft = f"{body} {signoff}"
        follow_up = "None — optional: note any small point raised for the team."
        escalation = False
    elif rating == 3:
        body = (
            f"{greet} We appreciate the honest feedback — we're glad "
            f"parts of {label} worked, and we hear you on the rest. "
            f"We'd love the chance to do better next time, so please "
            f"let us know how we can improve."
        )
        draft = f"{body} {signoff}"
        follow_up = "Owner/manager: read the full review and note the mixed point for the team."
        escalation = False
    elif rating == 2:
        body = (
            f"{greet} We're sorry {label} fell short — that's not the "
            f"experience we want to give. We take this seriously and "
            f"would like to make it right. Please reach out to us "
            f"directly so we can look into it."
        )
        draft = f"{body} {signoff}"
        follow_up = (
            "Owner/manager to contact the reviewer privately within 24 hours; "
            "do not debate the details in the public reply."
        )
        escalation = True
    else:  # rating == 1
        body = (
            f"{greet} We're very sorry — {label} should have been much "
            f"better, and we understand your frustration. We take this "
            f"seriously and would like the chance to make it right. "
            f"Please reach out to us directly so we can look into it."
        )
        draft = f"{body} {signoff}"
        follow_up = (
            "Owner/manager to contact the reviewer privately within 24 hours; "
            "investigate the specific issue before replying further."
        )
        escalation = True

    if any(w in review_text.lower() for w in ESCALATION_WORDS):
        escalation = True
        follow_up = (
            "ESCALATED: owner/manager to handle personally and promptly; "
            "do not reply publicly until the facts are checked. " + follow_up
        )

    draft = _enforce_length(draft)
    dont_say = [
        "Don't offer a discount, refund or freebie the owner hasn't approved.",
        "Don't name or blame individual staff members.",
        "Don't argue with the reviewer or dispute their account in public.",
        "Don't admit legal fault or make promises about outcomes.",
    ]
    if rating <= 2:
        dont_say.insert(0, "Don't copy-paste a generic apology — the draft above names the issue; keep it specific.")

    return {
        "draft_reply": draft,
        "draft_chars": len(draft),
        "rating": rating,
        "detected_topics": topics,
        "specific_detail_quoted": detail,
        "escalation_needed": escalation,
        "suggested_follow_up": follow_up,
        "do_not_say": dont_say,
        "human_review_required": rating <= 2,
    }


def classify(review_text: str, rating: int) -> dict:
    """Pure classification logic (no MCP) for triage."""
    _validate(rating, review_text, "x")
    lowered = review_text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in lowered)
    neg = sum(1 for w in NEGATIVE_WORDS if w in lowered)
    topics = _detect_topics(review_text)
    if rating >= 4:
        band = "positive"
    elif rating == 3:
        band = "mixed"
    else:
        band = "negative"
    sentiment = max(-1.0, min(1.0, (pos - neg) / 5.0 + (rating - 3) / 2.0))
    escalation = rating <= 2 or any(w in lowered for w in ESCALATION_WORDS)
    return {
        "band": band,
        "sentiment_score": round(sentiment, 2),
        "positive_signals": pos,
        "negative_signals": neg,
        "detected_topics": topics,
        "escalation_needed": escalation,
        "priority": "high" if escalation else ("medium" if band == "mixed" else "low"),
    }


@mcp.tool()
def draft_review_reply(
    review_text: str,
    rating: int,
    business_name: str,
    business_type: str = "",
    tone: str = "warm",
    reviewer_name: str = "",
) -> dict:
    """Draft a professional reply to a local-business review.

    Use for a single Google / local-business review. Returns a paste-ready
    reply under 600 characters, plus escalation flag, suggested follow-up
    and what-not-to-say guidance. Never invents discounts, staff names or
    promises. A human must read the draft before posting, especially for
    1-2 star reviews.
    """
    return build_draft(
        review_text=review_text,
        rating=rating,
        business_name=business_name,
        business_type=business_type,
        tone=tone,
        reviewer_name=reviewer_name,
    )


@mcp.tool()
def classify_review(review_text: str, rating: int) -> dict:
    """Classify a review for triage: positive / mixed / negative band, sentiment score, topics and escalation flag."""
    return classify(review_text=review_text, rating=rating)


if __name__ == "__main__":
    mcp.run()
