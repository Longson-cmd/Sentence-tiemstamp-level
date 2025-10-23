import json
import sys
from pydub import AudioSegment
import simpleaudio as sa

# ---- Load JSON file ----
with open("checkaudio.json", "r", encoding="utf-8") as file:
    sentence_timestamps = json.load(file)

if not sentence_timestamps:
    raise ValueError("❌ No timestamps found in checkaudio.json")

# ---- Get index from command line ----
if len(sys.argv) < 2:
    print(f"Usage: python c.py <index>")
    sys.exit(1)

try:
    idx = int(sys.argv[1])
except ValueError:
    print("⚠️ Index must be an integer.")
    sys.exit(1)

if not (0 <= idx < len(sentence_timestamps)):
    print(f"⚠️ Index out of range. Valid range: 0–{len(sentence_timestamps)-1}")
    sys.exit(1)

# ---- Select the sentence ----
s = sentence_timestamps[idx]
start = s["start"]
end = s["end"]
text = s["text"]

print(f"\n▶️ Playing sentence {idx}:")
print(f"Text : {text}")
print(f"Start: {start}s, End: {end}s")

# ---- Load and play audio ----
audio = AudioSegment.from_file("test1.mp3", format="mp3")
segment = audio[start * 1000 : end * 1000]

play_obj = sa.play_buffer(
    segment.raw_data,
    num_channels=segment.channels,
    bytes_per_sample=segment.sample_width,
    sample_rate=segment.frame_rate
)
play_obj.wait_done()

print("\n✅ Done playing.")
