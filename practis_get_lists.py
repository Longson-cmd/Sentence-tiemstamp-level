import json 
import re
import unicodedata


i = 2
# -----------GET DATA FROM TXT----------
with open(f"test/test{i}.txt", "r", encoding="utf-8") as f:
    text = f.read()

def clean_word(word):
    w = word.lower().strip()
    w = unicodedata.normalize("NFKD", w)
    w = w.replace("’" , "'").replace("–" , "-").replace("—" , "-")
    w = re.sub(r"[^\w\s']", "", w)
    return w

def get_sentence_lists(text):
    t = text.replace('\r\n', '\n').replace('\r', '\n').strip()
    paras = re.split(r"\n+", t)
    paras = [para.strip() for para in paras if para.strip()]

    one_dimention_sentence_list = []
    two_dimention_sentence_list = []

    for p in paras:
        p = re.sub(r"\s+([?.!])", r"\1", p)
        p = re.sub(r"([!?.]+)", r"\1<S>", p)
        p = re.sub(r"[ \t]+", " ", p)
        sens = [s.strip() for s in p.split("<S>") if s.strip()]

        one_dimention_sentence_list.extend(sens)
        two_dimention_sentence_list.append(sens)

    return one_dimention_sentence_list, two_dimention_sentence_list
one_dimention_sentence_list, two_dimention_sentence_list = get_sentence_lists(text)

list_id = []
list_ref = []
for s_idx, sentence in enumerate(one_dimention_sentence_list):
    for w_idx, word in enumerate(sentence.split()):
        list_id.append((word, (w_idx, s_idx)))
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

for item in data:
    start_sentence = item["start"]
    end_sentence = item["end"]
    list_words = [clean_word(w) for w in item["text"].split()]
    if len(list_words)!= 0:
        gap = (end_sentence - start_sentence) / len(list_words)
    else:
        gap = 1

    for i, word in enumerate(list_words):
        whisper.append(word)
        wordtimestamp.append(
            {
            "start": round(start_sentence + gap * i, 2),
            "end": round(start_sentence + gap * (i+1), 2)}
        )

with open('compareTwo.json', 'w', encoding='utf-8') as f:
    json.dump({"whisper_list_word": whisper, "whisper_time_stamp" : wordtimestamp}, f, indent=4)