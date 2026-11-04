# YouTube → MP3

A tiny GUI app that downloads a YouTube video's audio and converts it to MP3.

## Why this instead of an online converter?

- **Better quality.** It pulls the original audio stream and encodes straight to 192 kbps MP3 with ffmpeg — no lossy re-compression on someone else's server. Online converters often downmix to low bitrates or re-encode an already-degraded copy.
- **No guessing which site to trust.** Online "YouTube to MP3" sites are a roulette wheel of pop-ups, fake download buttons, and shady uploads. This is a local tool you can read and run yourself.
- **Faster, no ads.** Downloads go directly to your machine — no waiting in a queue, no ads, no captchas, no redirects.
- **Private.** Your URL never leaves your computer.

## Requirements

- Python 3.9+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/) on your `PATH` (required for MP3 conversion)
- Tkinter (bundled with Python on Windows and macOS; on Linux install it separately, e.g. `sudo apt install python3-tk`)

## Install

```
pip install -r requirements.txt
```

Install ffmpeg and make sure it's on your `PATH`. On Windows, `winget install ffmpeg` is the easiest option; on macOS, `brew install ffmpeg`; on Debian/Ubuntu, `sudo apt install ffmpeg`.

## Run

On Windows, double-click `youtube_to_mp3.pyw` (runs without a console window), or:

```
python youtube_to_mp3.pyw
```

Paste a YouTube URL and click **Extract Audio**.

## Output location

By default files are saved to `~/Music/Youtube Converted Audio` (created automatically). Click the **Change save folder…** button in the app to choose a different folder — your choice is remembered between sessions (stored in `~/.youtube_mp3_config.json`). You can also set the `YOUTUBE_MP3_DIR` environment variable to override it.

## Note

This is for downloading audio you have the rights to download.
