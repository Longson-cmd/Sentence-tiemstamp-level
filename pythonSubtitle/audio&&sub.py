from yt_dlp import YoutubeDL

URL = "https://www.youtube.com/watch?v=N0gZFvpxNhQ&t=10s"
LANGS = ["en"]  # preferred subtitle languages

ydl_opts = {
    # --- audio download ---
    "format": "bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],

    # --- subtitle download ---
    "writesubtitles": True,           # download subtitles if available
    "writeautomaticsub": True,        # fall back to auto-generated subtitles
    "subtitleslangs": LANGS,          # subtitle language(s)
    "subtitlesformat": "vtt",         # save format (.vtt keeps timestamps)

    # --- general ---
    "merge_output_format": None,      # don't merge audio/video
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=True)  # download audio + subtitles

print("Done. Check the folder: you should have an .mp3 file and a .vtt subtitle file.")
