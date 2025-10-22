import json
import re
import unicodedata

with open('result.json', encoding='utf-8') as f:
    data = json.load(f)['segments']

def clean_word(word: str) -> str:
    """
    Clean a single English word for alignment use.

    Steps:
    - lowercase
    - normalize unicode (e.g., fancy quotes)
    - remove punctuation (.,!? etc.)
    - remove apostrophes ("I'm" -> "im")
    - remove extra spaces
    """
    # 1. lowercase and trim
    word = word.lower().strip()

    # 2. normalize unicode (so “I’m” -> "I'm")
    word = unicodedata.normalize("NFKD", word)
    word = word.replace("’", "'").replace("–", "-").replace("—", "-")

    # 3. remove punctuation (keep apostrophes for now)
    word = re.sub(r"[^\w\s']", "", word)

    # 4. remove apostrophes (so "I'm" -> "im")
    word = word.replace("'", "")

    # 5. return only if it has letters/numbers
    if not re.search(r"[a-z0-9]", word):
        return ""

    return word


wordtimestamp = []
whisper = []

def handleSentence(text, start, end):
    duration = end - start
    listwords = text.split(' ')
    listwords = [item for item in listwords if item != '']
    if len(listwords) != 0:
        gap = duration / len(listwords) 

    for i, word in enumerate(listwords):
        cls = clean_word(word)
        wordtimestamp.append({"word": cls, "start": round(start + gap * i, 2), "end": round(start + gap * (i+1), 2)})
        whisper.append(cls)
for k in range(len(data)):
    handleSentence(data[k]["text"], data[k]["start"], data[k]["end"])


with open('compareTwo.json', 'w', encoding='utf-8') as f:
    json.dump({"whisper_list_word": whisper, "whisper_time_stamp" : wordtimestamp}, f, indent=4)