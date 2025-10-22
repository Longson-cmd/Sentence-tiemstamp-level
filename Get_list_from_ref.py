import json
import re
import unicodedata

with open("demo.txt", "r", encoding="utf-8") as f:
    text = f.read()


def clean_word(word: str) -> str:
    """Làm sạch 1 từ (dành cho tiếng Anh)."""
    word = word.lower().strip()
    word = unicodedata.normalize("NFKD", word)
    word = word.replace("’", "'").replace("–", "-").replace("—", "-")
    word = re.sub(r"[^\w\s']", "", word)
    word = word.replace("'", "")
    return word if re.search(r"[a-z0-9]", word) else ""


def split_into_paragraph_sentences(text: str):
    """
    Tách đoạn văn thành mảng 2 chiều:
    - Mỗi đoạn (ngăn cách bởi dòng trống) là một mảng con.
    - Mỗi mảng con chứa các câu (ngăn cách bởi ., !, ?, hoặc xuống dòng).
    """
    # Chuẩn hóa newline
    t = text.replace('\r\n', '\n').replace('\r', '\n').strip()

    # Chia đoạn theo dòng trống (ít nhất 1 dòng trống)
    paragraphs = re.split(r'\n\s*\n+', t)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    sentences_in_para = []

    for p in paragraphs:
        # Xóa khoảng trắng trước dấu câu
        p = re.sub(r'\s+([.!?])', r'\1', p)

        # Chèn mốc sau dấu câu
        p = re.sub(r'([.!?])', r'\1<S>', p)

        # Gom nhiều khoảng trắng thành 1
        p = re.sub(r'[ \t]+', ' ', p)

        # Tách thành danh sách câu
        sens = [s.strip() for s in p.split('<S>') if s.strip()]
        sentences_in_para.append(sens)

    return paragraphs, sentences_in_para

paragraphs, sentences_in_para = split_into_paragraph_sentences(text)
sentences = [s for sublist in sentences_in_para for s in sublist]
list_reference = []
list_id = []
for s, sent in enumerate(sentences):
    list_words = [clean_word(w) for w in sent.split() if clean_word(w) != '']

    for w, word in enumerate(list_words):
        list_id.append((word, (w, s)))
        list_reference.append(word)
        # print((word, (w, s)))
# Wrap it in a dict with key "ref"
data = {"ref": list_reference, "ref_id": list_id}

with open('compareOne.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)