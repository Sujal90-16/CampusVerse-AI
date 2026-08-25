from enum import Enum


class Intent(str, Enum):
    """High-level intent categories understood by SHAAN."""

    TIMETABLE = "timetable"
    ATTENDANCE = "attendance"
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    NOTICE = "notice"
    EVENT = "event"
    CLUB = "club"
    PLACEMENT = "placement"
    POLICY = "policy"
    ACADEMIC = "academic"
    FACILITY = "facility"
    FEEDBACK = "feedback"
    GENERAL_CAMPUS = "general_campus"
    GENERAL = "general"


KEYWORDS: dict[Intent, tuple[str, ...]] = {
    Intent.TIMETABLE: (
        "timetable",
        "time table",
        "schedule",
        "class",
        "lecture",
        "period",
        "meri class",
        "kaunsi class",
    ),

    Intent.ATTENDANCE: (
        "attendance",
        "attendence",
        "present",
        "absent",
        "percentage",
        "meri attendance",
    ),

    Intent.ASSIGNMENT: (
        "assignment",
        "homework",
        "submission",
        "deadline",
        "submit",
    ),

    Intent.EXAM: (
        "exam",
        "examination",
        "semester exam",
        "mid sem",
        "mid-sem",
        "midsem",
        "test",
    ),

    Intent.NOTICE: (
        "notice",
        "circular",
        "announcement",
        "notification",
    ),

    Intent.EVENT: (
        "event",
        "workshop",
        "hackathon",
        "sports",
        "competition",
    ),

    Intent.CLUB: (
        "club",
        "society",
        "societies",
        "student club",
    ),

    Intent.PLACEMENT: (
        "placement",
        "job",
        "internship",
        "company",
        "drive",
        "campus placement",
    ),

    Intent.POLICY: (
        "policy",
        "rule",
        "rules",
        "regulation",
        "eligibility",
        "compulsory",
        "mandatory",
        "allowed",
    ),

    Intent.ACADEMIC: (
        "subject",
        "course",
        "syllabus",
        "faculty",
        "professor",
        "marks",
        "cgpa",
        "credit",
    ),

    Intent.FACILITY: (
        "library",
        "lab",
        "hostel",
        "canteen",
        "gym",
        "facility",
        "parking",
        "campus",
    ),

    Intent.FEEDBACK: (
        "feedback",
        "complaint",
        "issue",
        "problem",
        "suggestion",
    ),
}


# Higher-priority intents are checked first.
# This prevents domain words from incorrectly winning
# over policy or feedback questions.
PRIORITY: tuple[Intent, ...] = (
    Intent.POLICY,
    Intent.FEEDBACK,
)


def detect_intent(message: str) -> Intent:
    """
    Detect the most likely SHAAN intent from a user message.

    This is the first lightweight version of the classifier.
    Later, Gemini/LLM-based classification can be added as
    a fallback for ambiguous queries.
    """

    normalized = message.lower().strip()

    if not normalized:
        return Intent.GENERAL

    # Check high-priority intents first.
    for intent in PRIORITY:
        keywords = KEYWORDS.get(intent, ())

        if any(keyword in normalized for keyword in keywords):
            return intent

    # Check normal intents.
    for intent, keywords in KEYWORDS.items():

        if intent in PRIORITY:
            continue

        if any(keyword in normalized for keyword in keywords):
            return intent

    # If nothing matches, treat it as a general campus question.
    return Intent.GENERAL_CAMPUS