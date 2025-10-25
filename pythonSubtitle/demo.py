from yt_dlp import YoutubeDL

URL = "https://www.youtube.com/watch?v=N0gZFvpxNhQ&t=10s"
LANGS = ["en"]  # order of preference

ydl_opts = {
    "skip_download": True,            # don’t download the video
    "writesubtitles": True,           # write subtitles if available
    "writeautomaticsub": True,        # fall back to auto-generated
    "subtitleslangs": LANGS,          # pick your preferred languages
    "subtitlesformat": "vtt",         # save as .vtt
    "outtmpl": "%(title)s.%(ext)s",   # output file name template
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)
    # trigger subtitle download
    ydl.download([URL])

print("Done. Check the current folder for a .vtt file.")
