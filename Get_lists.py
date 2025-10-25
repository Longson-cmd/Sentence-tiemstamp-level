"""
=========================================
Text & Whisper Alignment Preprocessor
=========================================
Purpose:
    Process a text transcript and a Whisper ASR result file
    to generate two comparable datasets:
      1. Reference text data (cleaned words + sentence structure)
      2. Whisper output (cleaned words + estimated word timestamps)

Workflow:
    1. Read the input text (.txt) file.
    2. Clean and normalize each word.
    3. Split text into sentences and paragraphs.
    4. Save cleaned reference data as JSON.
    5. Read Whisper result (.json).
    6. Estimate timestamps for each word.
    7. Save Whisper output as JSON.

Author: (your name)
Date: (today’s date)
"""

import json
import re
import unicodedata


# ======================================
# 1. Load and preprocess raw text
# ======================================

i = 2  # file index for test/test{i}.txt and test/result{i}.json

# Read text file
with open(f"test/test{i}.txt", "r", encoding="utf-8") as f:
    text = f.read()


def clean_word(word: str) -> str:
    """
    Normalize and clean a single English word.

    Steps:
        - Lowercase and strip whitespace.
        - Normalize Unicode (NFKD) for consistent accents and symbols.
        - Replace smart quotes and various dash symbols.
        - Remove non-alphanumeric characters except apostrophes.

    Returns:
        str: cleaned word
    """
    w = word.lower().strip()
    w = unicodedata.normalize("NFKD", w)
    w = w.replace("’", "'").replace("–", "-").replace("—", "-")
    w = re.sub(r"[^\w\s']", "", w)
    return w


def get_sentence_lists(text: str):
    """
    Split raw text into lists of sentences.

    Args:
        text (str): the input text (may contain multiple paragraphs)

    Returns:
        tuple:
            - one_dimention_sentence_list (list[str]):
              flat list of all sentences across paragraphs
            - two_dimention_sentence_list (list[list[str]]):
              list of paragraphs, each containing a list of sentences
    """
    # Normalize newlines and trim whitespace
    t = text.replace('\r\n', '\n').replace('\r', '\n').strip()

    # Split by blank lines into paragraphs
    paras = re.split(r"\n+", t)
    paras = [para.strip() for para in paras if para.strip()]

    one_dimention_sentence_list = []
    two_dimention_sentence_list = []

    # Process each paragraph
    for p in paras:
        # Clean spacing before punctuation
        p = re.sub(r"\s+([?.!])", r"\1", p)
        # Mark sentence endings temporarily with <S>
        p = re.sub(r"([!?.]+)", r"\1<S>", p)
        # Normalize multiple spaces/tabs
        p = re.sub(r"[ \t]+", " ", p)

        # Split paragraph into sentences
        sens = [s.strip() for s in p.split("<S>") if s.strip()]

        # Collect results
        one_dimention_sentence_list.extend(sens)
        two_dimention_sentence_list.append(sens)

    return one_dimention_sentence_list, two_dimention_sentence_list


# Generate sentence lists
one_dimention_sentence_list, two_dimention_sentence_list = get_sentence_lists(text)


# ======================================
# 2. Build cleaned reference data
# ======================================

list_id = []   # list of tuples: (word, (word_index, sentence_index))
list_ref = []  # list of cleaned words only

for s_idx, sentence in enumerate(one_dimention_sentence_list):
    for w_idx, word in enumerate(sentence.split()):
        list_id.append((word, (w_idx, s_idx)))
        list_ref.append(clean_word(word))

# Wrap into dictionary for export
data_ref = {"ref": list_ref, "ref_id": list_id}

# Save reference data as JSON
with open('compareOne.json', 'w', encoding='utf-8') as f:
    json.dump(data_ref, f, indent=4)


# ======================================
# 3. Process Whisper transcription result
# ======================================

# Load Whisper JSON file
with open(f'test/result{i}.json', encoding='utf-8') as f:
    data = json.load(f)['segments']

whisper_wordtimestamp = []  # list of word timestamp dictionaries
whisper = []                # list of cleaned words

for item in data:
    start_sentence = item["start"]
    end_sentence = item["end"]
    list_words = [clean_word(w) for w in item["text"].split()]

    # If Whisper provides a segment with no words, assign a default gap
    if len(list_words) != 0:
        gap = (end_sentence - start_sentence) / len(list_words)
    else:
        gap = 1

    # Distribute timestamps evenly across words in the segment
    for i, word in enumerate(list_words):
        whisper.append(word)
        whisper_wordtimestamp.append(
            {
                "word": word,
                "start": round(start_sentence + gap * i, 2),
                "end": round(start_sentence + gap * (i + 1), 2),
            }
        )

# Save Whisper results as JSON
with open('compareTwo.json', 'w', encoding='utf-8') as f:
    json.dump(
        {"whisper_list_word": whisper, "whisper_time_stamp": whisper_wordtimestamp},
        f,
        indent=4,
    )
