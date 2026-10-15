#!/usr/bin/env python3
import fitz       # pip install pymupdf
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────
PDF_DIR         = Path("/Users/mainmarketing/Desktop/mass-of-the-dead")  # your folder
OUTPUT_IN_PLACE = True   # False → writes to a stamped/ subfolder
FOOTER_HEIGHT   = 20     # points
MARGIN_BOTTOM   = 10     # points above bottom edge
FONT_FILE       = "/System/Library/Fonts/Times.ttc"  # adjust if needed
FONTSIZE        = 16     # ← now 16 pt
TEXT            = "WWW.MYLATINMASS.COM"
# ────────────────────────────────────────────────────────────────────────────────

def stamp_footer(pdf_path: Path):
    doc = fitz.open(pdf_path)
    for page in doc:
        w, h = page.rect.width, page.rect.height
        footer_rect = fitz.Rect(
            0,
            h - MARGIN_BOTTOM - FOOTER_HEIGHT,
            w,
            h - MARGIN_BOTTOM
        )
        page.insert_textbox(
            footer_rect,
            TEXT,
            fontsize=FONTSIZE,
            fontfile=FONT_FILE,
            align=1  # 0=left, 1=center, 2=right
        )

    if OUTPUT_IN_PLACE:
        doc.save(
            pdf_path,
            incremental=True,
            encryption=fitz.PDF_ENCRYPT_KEEP
        )
    else:
        stamped_dir = pdf_path.parent / "stamped"
        stamped_dir.mkdir(exist_ok=True)
        out_path = stamped_dir / pdf_path.name
        doc.save(out_path)
    doc.close()
    print(f"Stamped: {pdf_path.name}")

def main():
    for pdf_file in PDF_DIR.glob("*.pdf"):
        stamp_footer(pdf_file)

if __name__ == "__main__":
    main()
