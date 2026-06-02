"""
clarifier.py
Detects genuinely ambiguous queries and asks the user to clarify
before passing to the model. Improves accuracy on vague inputs.
"""

import re
from typing import Optional


# Terms that need clarification with follow-up options
CLARIFICATION_MAP = {
    "recent|recently|latest|new": {
        "question": "How recent do you mean?",
        "options": ["Last 7 days", "Last 30 days", "Last 3 months", "This year"],
    },
    "popular|trending|most used": {
        "question": "How should I measure popularity?",
        "options": ["By count/frequency", "By rating", "By revenue", "By views"],
    },
    "big|large|huge|small|tiny": {
        "question": "Are you referring to quantity or size?",
        "options": ["Highest value/amount", "Most records", "Largest file/size"],
    },
    "good|bad|best|worst": {
        "question": "What metric defines 'best' here?",
        "options": ["Highest rating", "Most sales", "Lowest price", "Most reviews"],
    },
}


class Clarifier:
    def needs_clarification(self, question: str) -> Optional[dict]:
        """
        Check if question has vague terms needing clarification.
        Returns clarification dict or None if question is clear enough.
        """
        q_lower = question.lower()
        for pattern, clarification in CLARIFICATION_MAP.items():
            if re.search(pattern, q_lower):
                return clarification
        return None

    def refine_question(self, original: str, clarification_choice: str) -> str:
        """
        Inject the user's clarification choice back into the question
        to make it more specific for the model.
        """
        # Replace vague terms with the specific choice
        replacements = {
            "recent": clarification_choice,
            "recently": f"in the {clarification_choice}",
            "latest": clarification_choice,
            "popular": f"by {clarification_choice}",
            "best": f"with {clarification_choice}",
            "worst": f"with lowest {clarification_choice}",
        }
        refined = original
        for vague, specific in replacements.items():
            refined = re.sub(rf"\b{vague}\b", specific, refined, flags=re.IGNORECASE)
        return refined