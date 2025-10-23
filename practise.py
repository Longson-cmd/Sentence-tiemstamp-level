import json

# -----------GET DATA WHISPER RESULT------------
i = 1
with open(f'test/result{i}.json', encoding='utf-8') as f:
    data = json.load(f)['segments']

wordtimestamp = []
whisper = []

for items in data:
    whisper.append()