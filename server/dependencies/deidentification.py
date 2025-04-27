
import re

def deidentify_text(text: str) -> str:
    # Replace names (simple placeholder — can be smarter)
    text = re.sub(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", "[MY_NAME]", text)

    # Replace emails
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[MY_EMAIL]", text)

    # Replace phone numbers
    text = re.sub(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", "[MY_PHONE]", text)
    
    return text