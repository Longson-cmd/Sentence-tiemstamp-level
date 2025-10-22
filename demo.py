import re
import unicodedata

with open("demo.txt", "r", encoding="utf-8") as f:
    text = f.read()

def clean_words(text: str) :
    """
    Normalize and clean text into word tokens for alignment.
    Steps:
      1. Lowercase
      2. Remove punctuation/symbols
      3. Normalize unicode accents (optional)
      4. Split on whitespace
      5. Filter out empty tokens
    """
    # 1. lowercase
    text = text.lower().strip()

    # 2. normalize unicode (convert “é” → "e", “’” → "'")
    text = unicodedata.normalize("NFKD", text)

    # 3. replace fancy apostrophes and dashes
    text = text.replace("’", "'").replace("–", "-")

    # 4. remove punctuation (keep apostrophes inside words)
    # e.g. "let's" -> "lets"
    text = re.sub(r"[^\w\s']", " ", text)
    # optional: remove apostrophes entirely if you prefer
    text = text.replace("'", "")

    # 5. collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    # 6. split and remove empties
    words = [w for w in text.split(" ") if w]

    return words


print(clean_words(text))