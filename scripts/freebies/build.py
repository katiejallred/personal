#!/usr/bin/env python3
"""Print the free workbooks in this folder to PDF with headless Chromium.

Usage: python3 scripts/freebies/build.py
Writes assets/downloads/<name>.pdf for each source listed in BOOKS. Needs a
Chromium or Chrome binary; set CHROME=/path/to/chrome if it isn't found.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "assets" / "downloads"
BOOKS = {
    "90-day-plan.html": "katie-allred-90-day-plan-church-communications.pdf",
}


def find_chrome():
    candidates = [os.environ.get("CHROME"), "chromium", "chromium-browser",
                  "google-chrome", "chrome",
                  "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    for c in candidates:
        if c and (shutil.which(c) or Path(c).exists()):
            return shutil.which(c) or c
    sys.exit("Chromium not found; set CHROME=/path/to/chrome")


def main():
    chrome = find_chrome()
    OUT.mkdir(parents=True, exist_ok=True)
    for src, pdf in BOOKS.items():
        target = OUT / pdf
        subprocess.run([
            chrome, "--headless", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--allow-file-access-from-files",
            f"--print-to-pdf={target}", (HERE / src).as_uri(),
        ], check=True, capture_output=True)
        print(f"wrote {target.relative_to(ROOT)} ({target.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
