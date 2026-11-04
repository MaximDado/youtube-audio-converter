#!python3.11
import threading
import tkinter as tk
from tkinter import font
import yt_dlp

OUTPUT_DIR = r"C:\Users\Maxim\Music\Youtube Converted Audio"

COLORS = {
    "bg": "#1a1a2e",
    "surface": "#16213e",
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
        self._center(420, 210)
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
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        def progress_hook(d):
            if d["status"] == "downloading":
                pct = d.get("_percent_str", "").strip()
                self.after(0, self._set_status, f"Downloading… {pct}", COLORS["muted"])
            elif d["status"] == "finished":
                self.after(0, self._set_status, "Converting to MP3…", COLORS["muted"])

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{OUTPUT_DIR}/%(title)s.%(ext)s",
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
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "track")
                self.after(0, self._set_status, f'"{title[:40]}"…', COLORS["muted"])
                ydl.download([url])
            self.after(0, self._on_success)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _on_success(self):
        self._set_status("Saved to Music / Youtube Converted Audio", COLORS["success"])
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
