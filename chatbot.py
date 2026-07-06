"""
chatbot.py
==========
Rule-based NLP layer: keyword/intent detection and the chatbot's replies,
including the crisis / helpline messaging.
"""

import random

INTENT_KEYWORDS = {
    "greeting": ["hi", "hello", "hey", "salam", "assalam", "good morning", "good evening"],
    "sad": ["sad", "depressed", "down", "unhappy", "cry", "crying", "hopeless", "empty", "low"],
    "anxious": ["anxious", "anxiety", "nervous", "worried", "panic", "overwhelmed"],
    "stressed": ["stress", "stressed", "pressure", "burnt out", "burnout", "exhausted"],
    "lonely": ["lonely", "alone", "isolated", "no one understands", "no friends"],
    "angry": ["angry", "frustrated", "irritated", "annoyed", "mad"],
    "happy": ["happy", "good", "great", "fine", "okay", "ok", "well", "excited", "grateful"],
    "sleep": ["sleep", "insomnia", "tired", "can't sleep", "cant sleep"],
    "suicidal": ["suicide", "kill myself", "end my life", "want to die", "self harm", "hurt myself"],
    "thanks": ["thanks", "thank you", "shukriya"],
    "bye": ["bye", "goodbye", "exit", "quit", "see you"],
}

BOT_RESPONSES = {
    "greeting": [
        "Hello! I'm really glad you're here. How have you been feeling lately?",
        "Hi there! What's been on your mind recently?",
    ],
    "sad": [
        "I'm sorry you're feeling this way — that sounds heavy to carry. "
        "Would a short, confidential check-in help? Try the Depression screening "
        "from the panel on the left.",
    ],
    "anxious": [
        "It sounds like your mind has been racing. That's exhausting. "
        "The Anxiety screening on the left might help put words to what "
        "you're experiencing.",
    ],
    "stressed": [
        "That sounds like a lot of pressure to be under. Let's see how "
        "intense it really is — try the Stress screening whenever you're ready.",
    ],
    "lonely": [
        "Feeling disconnected from others is really painful. You reaching out "
        "here, right now, already says something good about you.",
    ],
    "angry": [
        "That frustration sounds valid. Do you want to talk about what "
        "triggered it?",
    ],
    "happy": [
        "That's wonderful to hear! What's been going well for you?",
    ],
    "sleep": [
        "Poor sleep can really affect mood and focus. How many nights this "
        "week have you had trouble sleeping?",
    ],
    "suicidal": [
        "I'm genuinely concerned about what you just shared. You matter, and "
        "you don't have to face this alone. Please contact a crisis helpline, "
        "a trusted person, or your nearest emergency room right now.",
    ],
    "thanks": [
        "You're always welcome. I'm glad I could help, even a little.",
    ],
    "bye": [
        "Take care of yourself. Reaching out for support is a sign of "
        "strength. I'll be here whenever you need to talk again.",
    ],
    "default": [
        "I hear you. Can you tell me a little more about that?",
        "Thank you for sharing that. How long have you been feeling this way?",
        "That makes sense given what you're going through. Would one of the "
        "screenings on the left help you understand it better?",
    ],
}

CRISIS_MESSAGE = (
    "If you are in immediate danger, please contact your local emergency "
    "number right now.\nYou can also reach a mental health helpline in your "
    "country for free, confidential support."
)

HELPLINE_INFO = (
    "💙 You don't have to go through this alone. Please reach out:\n\n"
    "🇵🇰 Pakistan:\n"
    "   • Umang Pakistan Helpline: 0311-7786264\n"
    "   • Rozan Helpline: 0304-111-1741\n"
    "🇮🇳 India: iCall — 9152987821\n"
    "🇺🇸 USA/Canada: 988 (Suicide & Crisis Lifeline)\n"
    "🇬🇧 UK & Ireland: Samaritans — 116 123\n"
    "🌍 Other countries: befrienders.org\n\n"
    "If you are in immediate danger, please contact your local emergency "
    "number right now."
)


def detect_intent(text: str) -> str:
    text = text.lower()
    for word in INTENT_KEYWORDS["suicidal"]:
        if word in text:
            return "suicidal"
    for intent, words in INTENT_KEYWORDS.items():
        if intent == "suicidal":
            continue
        if any(w in text for w in words):
            return intent
    return "default"


def get_bot_reply(text: str) -> str:
    intent = detect_intent(text)
    reply = random.choice(BOT_RESPONSES[intent])
    if intent == "suicidal":
        reply += "\n\n" + HELPLINE_INFO
    return reply
