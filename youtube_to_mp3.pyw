#!python3.11
import json
import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, font

import yt_dlp

DEFAULT_DIR = Path.home() / "Music" / "Youtube Converted Audio"
CONFIG_PATH = Path.home() / ".youtube_mp3_config.json"


def _load_saved_dir():
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("output_dir")
        if raw:
            return Path(raw).expanduser()
    except Exception:
        pass
    return DEFAULT_DIR


def _save_dir(path):
    try:
        CONFIG_PATH.write_text(json.dumps({"output_dir": str(path)}), encoding="utf-8")
    except OSError:
        pass


_env_dir = os.environ.get("YOUTUBE_MP3_DIR")
OUTPUT_DIR = Path(_env_dir) if _env_dir else _load_saved_dir()

COLORS = {
    "bg": "#1a1a2e",
    "surface": "#16213e",
    "surface_hover": "#2a3b63",
    "accent": "#e94560",
    "text": "#eaeaea",
    "muted": "#8892a4",
    "success": "#4caf50",
    "entry_bg": "#0f3460",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube → MP3")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])
        self._center(420, 245)
        self._tip = None
        self._build()

    def _center(self, w, h):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build(self):
        px = 24

        title_font = font.Font(family="Segoe UI", size=13, weight="bold")
        label_font = font.Font(family="Segoe UI", size=9)
        entry_font = font.Font(family="Segoe UI", size=10)
        btn_font   = font.Font(family="Segoe UI", size=10, weight="bold")

        tk.Label(self, text="YouTube → MP3", bg=COLORS["bg"],
                 fg=COLORS["text"], font=title_font).pack(pady=(20, 4))

        tk.Label(self, text="Paste a YouTube URL and click Extract Audio",
                 bg=COLORS["bg"], fg=COLORS["muted"], font=label_font).pack()

        self.url_var = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.url_var, font=entry_font,
                         bg=COLORS["entry_bg"], fg=COLORS["text"],
                         insertbackground=COLORS["text"],
                         relief="flat", bd=0, highlightthickness=1,
                         highlightbackground=COLORS["muted"],
                         highlightcolor=COLORS["accent"])
        entry.pack(fill="x", padx=px, pady=(12, 0), ipady=6)
        entry.bind("<Return>", lambda _: self._start())

        self.btn = tk.Button(self, text="Extract Audio", font=btn_font,
                             bg=COLORS["accent"], fg="white", activebackground="#c73652",
                             activeforeground="white", relief="flat", bd=0,
                             cursor="hand2", command=self._start)
        self.btn.pack(fill="x", padx=px, pady=(10, 0), ipady=7)

        self.folder_btn = tk.Button(self, text="Change save folder…", font=label_font,
                                    bg=COLORS["surface"], fg=COLORS["muted"],
                                    activebackground=COLORS["surface_hover"],
                                    activeforeground=COLORS["text"],
                                    relief="flat", bd=0, cursor="hand2",
                                    command=self._change_dir)
        self.folder_btn.pack(fill="x", padx=px, pady=(6, 0), ipady=4)
        self.folder_btn.bind("<Enter>", self._show_tooltip)
        self.folder_btn.bind("<Leave>", self._hide_tooltip)

        self.status = tk.Label(self, text="", bg=COLORS["bg"],
                               fg=COLORS["muted"], font=label_font)
        self.status.pack(pady=(8, 0))

    def _start(self):
        url = self.url_var.get().strip()
        if not url:
            self._set_status("Please enter a URL.", COLORS["accent"])
            return
        self.btn.config(state="disabled", text="Downloading…")
        self._set_status("Fetching info…", COLORS["muted"])
        threading.Thread(target=self._prepare, args=(url,), daemon=True).start()

    def _prepare(self, url):
        if shutil.which("ffmpeg") is None:
            self.after(0, self._on_error,
                       "ffmpeg not found. Install it and add it to your PATH.")
            return

        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.after(0, self._on_error, f"Can't create output folder: {e}")
            return

        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "track")
        except Exception as e:
            self.after(0, self._on_error, str(e))
            return

        self.after(0, self._begin_download, url, title)

    def _begin_download(self, url, title):
        self._set_status(f'"{title[:40]}"…', COLORS["muted"])
        threading.Thread(target=self._download, args=(url, OUTPUT_DIR), daemon=True).start()

    def _change_dir(self):
        self._hide_tooltip(None)
        global OUTPUT_DIR
        chosen = filedialog.askdirectory(
            title="Choose save folder",
            initialdir=str(OUTPUT_DIR),
        )
        if not chosen:
            return
        OUTPUT_DIR = Path(chosen)
        _save_dir(OUTPUT_DIR)

    def _show_tooltip(self, event):
        self._hide_tooltip(None)
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        self._tip = tk.Toplevel(self)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self._tip, text=f"Saves to:\n{OUTPUT_DIR}\n\nClick to change",
                 bg="#0f0f17", fg=COLORS["text"], font=("Segoe UI", 9),
                 justify="left", padx=10, pady=8).pack()

    def _hide_tooltip(self, event):
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None

    def _download(self, url, outdir):
        def progress_hook(d):
            if d["status"] == "downloading":
                pct = d.get("_percent_str", "").strip()
                self.after(0, self._set_status, f"Downloading… {pct}", COLORS["muted"])
            elif d["status"] == "finished":
                self.after(0, self._set_status, "Converting to MP3…", COLORS["muted"])

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(Path(outdir) / "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "progress_hooks": [progress_hook],
            "extractor_args": {"youtube": {"player_client": ["android", "ios", "web"]}},
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_success, outdir)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_success(self, outdir=OUTPUT_DIR):
        self._set_status(f"Saved to {outdir}", COLORS["success"])
        self.btn.config(state="normal", text="Extract Audio")
        self.url_var.set("")

    def _on_error(self, msg):
        msg = msg.removeprefix("ERROR: ").strip()
        short = msg[:80] if len(msg) > 80 else msg
        self._set_status(f"Error: {short}", COLORS["accent"])
        self.btn.config(state="normal", text="Extract Audio")

    def _set_status(self, text, color):
        self.status.config(text=text, fg=color)


if __name__ == "__main__":
    App().mainloop()
