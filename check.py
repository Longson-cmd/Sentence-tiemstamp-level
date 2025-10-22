import re

def clean_text(text):
    text = re.sub(r"[ /t]+", " ", text)
    text = "\n".join([line.strip() for line in text.splitlines() if line != ""])
    return text


with open('demo.txt', "r", encoding="utf-8") as f:
    text = f.read()

new_text = clean_text(text)

with open("check.txt", "w", encoding="utf-8") as f:
    f.write(new_text)