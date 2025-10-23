import json
import re
import unicodedata

i=1

with open(f"test/test{i}.txt", "r", encoding="utf-8") as f:
    text = f.read()

def clean_word(word: str) -> str:
    """Làm sạch 1 từ (dành cho tiếng Anh)."""
    word = word.lower().strip()
    word = unicodedata.normalize("NFKD", word)
    word = word.replace("’", "'").replace("–", "-").replace("—", "-")
    word = re.sub(r"[^\w\s']", "", word)
    return word


def split_into_paragraph_sentences(text: str):
    """
    Tách đoạn văn thành mảng 2 chiều:
    - Mỗi đoạn (ngăn cách bởi newline) là một mảng con.
    - Mỗi mảng con chứa các câu (ngăn cách bởi ., !, ?, hoặc xuống dòng).
    """
    # Chuẩn hóa newline
    t = text.replace('\r\n', '\n').replace('\r', '\n').strip()


    paragraphs = re.split(r'\n+', t)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]


    sentences_in_para = []
    sentences = []
    for p in paragraphs:
        # Xóa khoảng trắng trước dấu câu
        p = re.sub(r'\s+([.!?])', r'\1', p)

        # Chèn mốc sau dấu câu
        p = re.sub(r'([.!?]+)', r'\1<S>', p)

        # Gom nhiều khoảng trắng thành 1
        p = re.sub(r'[ \t]+', ' ', p)

        # Tách thành danh sách câu
        sens = [s.strip() for s in p.split('<S>') if s.strip()]
        sentences_in_para.append(sens)
        sentences.extend(sens)
    return sentences_in_para, sentences
sentences_in_para, sentences = split_into_paragraph_sentences(text)

list_ref = []
list_id = []

for s, sent in enumerate(sentences):
    # print(s)
    # print(sent)
    list_words = [w for w in sent.split() ]

    for w, word in enumerate(list_words):
        list_id.append((word, (w, s)))
        list_ref.append(clean_word(word))
# Wrap it in a dict with key "ref"
data_ref = {"ref": list_ref, "ref_id": list_id}
with open('compareOne.json', 'w', encoding='utf-8') as f:
    json.dump(data_ref, f, indent=4)
# -----------GET DATA WHISPER RESULT------------

with open(f'test/result{i}.json', encoding='utf-8') as f:
    data = json.load(f)['segments']

wordtimestamp = []
whisper = []

def handleSentence(text, start, end):
    duration = end - start
    listwords = text.split()
    listwords = [item for item in listwords if item != '']
    if len(listwords) != 0:
        gap = duration / len(listwords) 
    else:
        gap = 1
    for i, word in enumerate(listwords):
        cls = clean_word(word)
        wordtimestamp.append({"word": cls, "start": round(start + gap * i, 2), "end": round(start + gap * (i+1), 2)})
        whisper.append(cls)
for k in range(len(data)):
    handleSentence(data[k]["text"], data[k]["start"], data[k]["end"])

with open('compareTwo.json', 'w', encoding='utf-8') as f:
    json.dump({"whisper_list_word": whisper, "whisper_time_stamp" : wordtimestamp}, f, indent=4)