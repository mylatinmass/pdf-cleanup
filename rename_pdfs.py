#!/usr/bin/env python3
import fitz         # pip install pymupdf
import re
import shutil
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
PDF_DIR    = Path("/Users/mainmarketing/Desktop/mass-of-the-dead")  # ← your folder
OUTPUT_DIR = PDF_DIR / "FINAL"                                   # ← where renamed copies go
# ────────────────────────────────────────────────────────────────────────────────

def sanitize_filename(s: str) -> str:
    """Strip out filesystem-illegal chars and collapse whitespace."""
    s = re.sub(r'[\\/:"*?<>|]+', "", s)
    return re.sub(r"\s+", " ", s).strip()

def get_first_line(pdf_path: Path) -> str:
    """Grab the very first non-blank line of text on page 1."""
    doc = fitz.open(pdf_path)
    text = doc[0].get_text("text")
    doc.close()
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return None

def unique_target(path: Path) -> Path:
    """
    If `path` doesn't exist, return it.
    Otherwise, append (1), (2), ... before the extension until unique.
    """
    if not path.exists():
        return path

    base, ext = path.stem, path.suffix
    i = 1
    while True:
        candidate = path.parent / f"{base} ({i}){ext}"
        if not candidate.exists():
            return candidate
        i += 1

def rename_to_final(folder: Path):
    OUTPUT_DIR.mkdir(exist_ok=True)
    for pdf_path in folder.glob("*.pdf"):
        title = get_first_line(pdf_path)
        if not title:
            print(f"⚠️  No text in {pdf_path.name}; skipping.")
            continue

        safe = sanitize_filename(title)
        initial = OUTPUT_DIR / f"{safe}.pdf"
        target = unique_target(initial)

        # copy original → FINAL/<unique name>.pdf
        shutil.copy2(pdf_path, target)
        print(f"✅  {pdf_path.name} → FINAL/{target.name}")

if __name__ == "__main__":
    rename_to_final(PDF_DIR)
