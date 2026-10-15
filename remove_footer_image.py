#!/usr/bin/env python3
import fitz       # PyMuPDF
import os
from pathlib import Path

# adjust as needed:
PDF_DIR = Path("/Users/mainmarketing/Desktop/pdf-holy-week")  # your folder of PDFs
BOTTOM_THRESHOLD = 0.8  # fraction of page height; anything below this line we'll consider "footer"

def remove_footer_image(pdf_path: Path):
    doc = fitz.open(pdf_path)
    page = doc[-1]  # last page
    page_rect = page.rect
    did_redact = False

    # scan text/image blocks
    for block in page.get_text("dict")["blocks"]:
        if block["type"] == 1:  # image block
            x0, y0, x1, y1 = block["bbox"]
            # only target images low on the page
            if y0 > page_rect.height * BOTTOM_THRESHOLD:
                rect = fitz.Rect(x0, y0, x1, y1)
                page.add_redact_annot(rect, fill=(1, 1, 1))  # white‐out
                did_redact = True

    if did_redact:
        if did_redact:
        # apply redactions on that last page
            page.apply_redactions(
            images=fitz.PDF_REDACT_IMAGE_PIXELS,          # blank out overlapping images
            graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,  # remove vectors
            text=fitz.PDF_REDACT_TEXT_REMOVE              # (default) remove any text
        )
        doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        print(f"✔ Removed footer image from {pdf_path.name}")
    else:
        print(f"— No footer image found in {pdf_path.name}")

    doc.close()

def main():
    for pdf_file in PDF_DIR.glob("*.pdf"):
        remove_footer_image(pdf_file)

if __name__ == "__main__":
    main()
