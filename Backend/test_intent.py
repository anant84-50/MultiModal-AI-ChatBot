import re
from app.services.llm_service import llm_service

def is_image_generation_intent(text: str) -> bool:
    patterns = [
        r'\b(?:generate|create|make|draw|paint|show me|produce)\b.*\b(?:image|photo|picture|wallpaper|portrait|illustration|drawing|pic|art|logo)\b',
        r'\b(?:image|photo|picture|pic|art)\b.*\b(?:of|for|with|showing)\b',
        r'\b(?:photo|image|picture|pic|tasveer|chitra|chhavi|banao|bana do|bana ke do)\b'
    ]
    t = text.lower()
    return any(re.search(p, t) for p in patterns)

tests = [
    "generate an image of a golden lion in neon cyberpunk city",
    "ek sher ki photo banao",
    "can you create a picture of sunset on the beach?",
    "what is photosynthesis?",
    "make an illustration of astronaut in space",
    "draw a beautiful anime girl with sword",
    "summarize this document",
    "show me an image of a red sports car",
    "photo banao taj mahal ki"
]

for q in tests:
    print(f"'{q}' -> is_img_gen: {is_image_generation_intent(q)}")
