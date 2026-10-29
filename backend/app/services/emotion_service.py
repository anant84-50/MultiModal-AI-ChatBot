import re
from typing import Tuple

CRISIS_KEYWORDS = [
    r"\bsuicide\b", r"\bkill myself\b", r"\bend my life\b", r"\bwant to die\b",
    r"\bhurt myself\b", r"\bself harm\b", r"\bcutting myself\b", r"\bno reason to live\b"
]

CRISIS_RESPONSE = """I can hear how much pain you are in right now, and I want you to be safe. Please know that you do not have to carry this alone. There are compassionate people ready to support you 24/7:

- **National Suicide & Crisis Lifeline**: Call or text **988** (Available 24 hours, free & confidential in the US/Canada)
- **Crisis Text Line**: Text **HOME** to **741741**
- **International Resources**: [Befrienders Worldwide](https://www.befrienders.org/) or [Find A Helpline](https://findahelpline.com/)
- **Emergency Services**: Please call your local emergency services (like 911 or 112) or go to the nearest emergency room.

Please reach out to one of these resources or a trusted family member or friend right now. Your life is important."""

EMOTIONAL_PROMPT_INSTRUCTION = """
You are also acting as a supportive, compassionate conversational partner.
Guidelines:
1. Listen attentively, validate the user's emotions, and respond with warmth and empathy.
2. Ask gentle, open-ended follow-up questions to help them reflect.
3. Suggest simple, healthy coping activities (e.g., box breathing, going for a short walk, journaling, talking to someone).
4. Maintain a clear, humble boundary: never claim to be a licensed therapist, clinical psychologist, or medical doctor. Do not diagnose mental health disorders.
5. Emphasize that seeking professional guidance or speaking with loved ones is a sign of strength.
"""

def detect_crisis_risk(text: str) -> bool:
    """Checks if the user input contains high-risk indicators of self-harm or suicide."""
    clean_text = text.lower()
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, clean_text):
            return True
    return False

def check_emotional_context(text: str) -> Tuple[bool, bool, str]:
    """
    Analyzes user text.
    Returns:
    (is_emotional, is_crisis, custom_safety_response)
    """
    if detect_crisis_risk(text):
        return (True, True, CRISIS_RESPONSE)
    
    emotional_triggers = [
        "sad", "depressed", "anxious", "lonely", "stress", "stressed", "overwhelmed",
        "heartbroken", "crying", "scared", "hopeless", "frustrated", "tired of everything",
        "grief", "breakup", "feeling down"
    ]
    lower = text.lower()
    is_emotional = any(trigger in lower for trigger in emotional_triggers)
    return (is_emotional, False, "")
