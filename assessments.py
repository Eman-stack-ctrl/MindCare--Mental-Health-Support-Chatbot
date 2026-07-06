"""
assessments.py
==============
Everything about the four screening tools: the answer scales, the
question sets, the scoring/interpretation logic, personalized coping
tips, journaling prompts, and small color helpers used by the charts
and journal.
"""

from theme import COLOR_PRIMARY

SCALE_4PT = [("Not at all", 0), ("Several days", 1),
             ("More than half the days", 2), ("Nearly every day", 3)]

SCALE_PSS = [("Never", 0), ("Almost never", 1), ("Sometimes", 2),
             ("Fairly often", 3), ("Very often", 4)]

SCALE_WHO5 = [("At no time", 0), ("Some of the time", 1), ("Less than half the time", 2),
              ("More than half the time", 3), ("Most of the time", 4), ("All of the time", 5)]


def interpret_phq9(score):
    if score <= 4: return "Minimal or no depression symptoms."
    if score <= 9: return "Mild depression symptoms."
    if score <= 14: return "Moderate depression symptoms."
    if score <= 19: return "Moderately severe depression symptoms."
    return "Severe depression symptoms."


def interpret_gad7(score):
    if score <= 4: return "Minimal anxiety."
    if score <= 9: return "Mild anxiety."
    if score <= 14: return "Moderate anxiety."
    return "Severe anxiety."


def interpret_pss4(score):
    if score <= 5: return "Low perceived stress."
    if score <= 10: return "Moderate perceived stress."
    return "High perceived stress."


def interpret_who5(score):
    # WHO-5 raw score (0-25) is conventionally scaled to 0-100
    pct = score * 4
    if pct >= 70: return f"Good wellbeing ({pct}/100)."
    if pct >= 50: return f"Fair wellbeing ({pct}/100)."
    return f"Low wellbeing ({pct}/100) - consider professional support."


ASSESSMENTS = {
    "phq9": {
        "name": "Depression Screening (PHQ-9 style)",
        "short": "Depression",
        "icon": "😔",
        "color": "#5c7ba8",
        "questions": [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling/staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself, or that you are a failure",
            "Trouble concentrating on things",
            "Moving/speaking slowly, or being fidgety/restless",
            "Thoughts that you would be better off dead, or hurting yourself",
        ],
        "options": SCALE_4PT,
        "max": 27,
        "interpret": interpret_phq9,
    },
    "gad7": {
        "name": "Anxiety Screening (GAD-7 style)",
        "short": "Anxiety",
        "icon": "😰",
        "color": "#2a9df4",
        "questions": [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen",
        ],
        "options": SCALE_4PT,
        "max": 21,
        "interpret": interpret_gad7,
    },
    "pss4": {
        "name": "Stress Screening (PSS-4 style)",
        "short": "Stress",
        "icon": "😣",
        "color": "#e0a458",
        "questions": [
            "Felt unable to control the important things in your life",
            "Felt confident about handling personal problems",
            "Felt that things were going your way",
            "Felt difficulties were piling up too high to overcome",
        ],
        "options": SCALE_PSS,
        "max": 16,
        "interpret": interpret_pss4,
    },
    "who5": {
        "name": "Wellbeing Index (WHO-5 style)",
        "short": "Wellbeing",
        "icon": "🌱",
        "color": "#2ec4b6",
        "questions": [
            "I have felt cheerful and in good spirits",
            "I have felt calm and relaxed",
            "I have felt active and vigorous",
            "I woke up feeling fresh and rested",
            "My daily life has been filled with things that interest me",
        ],
        "options": SCALE_WHO5,
        "max": 25,
        "interpret": interpret_who5,
    },
}

# ---- Personalized coping tips, keyed by assessment + severity band ----
COPING_TIPS = {
    "phq9": {
        "low": "You're doing okay on this one 🌤️ — keep up whatever's been helping (routine, people, hobbies).",
        "mid": "Small wins matter right now. Try doing just ONE small enjoyable thing today, even for 10 minutes.",
        "high": "Please be gentle with yourself. Consider reaching out to someone you trust today, even just to talk.",
    },
    "gad7": {
        "low": "Your anxiety seems manageable right now. Keep noticing what's helping you stay grounded.",
        "mid": "Racing thoughts are exhausting. Try grounding yourself — name 5 things you can see right now.",
        "high": "That's a lot of worry to carry. Try slowing your breathing down for a minute — in for 4 counts, out for 6.",
    },
    "pss4": {
        "low": "Stress is fairly low right now — nice. Keep protecting your downtime.",
        "mid": "You've got a lot on your plate. Try breaking today's tasks into smaller, manageable pieces.",
        "high": "This is a heavy load. A few minutes of slow breathing can help your body reset before you tackle the next thing.",
    },
    "who5": {
        "low": "Your wellbeing score is on the lower side. Even one small joyful activity today could help.",
        "mid": "There's room to feel better. What's one thing today that could bring a little more energy or calm?",
        "high": "Great to see — your wellbeing looks strong! Keep doing what's working for you.",
    },
}

JOURNAL_PROMPTS = {
    "phq9": "Before we move on — what's one thing that's been weighing on your mind today?",
    "gad7": "What's been the biggest source of worry for you this week?",
    "pss4": "What's been the biggest source of pressure on you lately?",
    "who5": "What's one small thing that made you smile or feel good recently?",
}


def get_severity_band(key, pct):
    """Returns 'low' / 'mid' / 'high' band. For who5, higher pct = better (band names flipped)."""
    if key == "who5":
        if pct >= 70: return "high"   # high wellbeing = good
        if pct >= 40: return "mid"
        return "low"
    else:
        if pct < 30: return "low"
        if pct < 65: return "mid"
        return "high"


def severity_color(pct):
    if pct < 25: return "#2ec4b6"     # good / low
    if pct < 50: return "#ffffff"     # mild
    if pct < 75: return "#f4a261"     # moderate
    return "#e63950"                  # high


def _color_for_short_name(short_name):
    for data in ASSESSMENTS.values():
        if data["short"] == short_name:
            return data["color"], data["icon"]
    return COLOR_PRIMARY, "📝"
