#!/usr/bin/env python3
# pip install PyMuPDF

import fitz
from pathlib import Path

# ————— CONFIG —————
FOOTER_TEXT  = "INSTITUTE OF CHRIST THE KING SOVEREIGN PRIEST"
WEBSITE_TEXT = "www.institute-christ-king.org"
# ———————————

def process_pdf(path: Path):
    doc = fitz.open(path)
    changed = False

    for page in doc:
        # redact the footer
        for r in page.search_for(FOOTER_TEXT):
            page.add_redact_annot(r, fill=(1,1,1))
            changed = True
        # redact the website URL
        for r in page.search_for(WEBSITE_TEXT):
            page.add_redact_annot(r, fill=(1,1,1))
            changed = True
        # commit redactions
        if page.first_annot:
            page.apply_redactions()

    if changed:
        tmp_path = path.with_suffix(path.suffix + ".tmp.pdf")
        doc.save(str(tmp_path))  # full rewrite to temp
        doc.close()

        # replace original with temp
        path.unlink()             # delete the original
        tmp_path.rename(path)     # move temp into its place
        print(f"   ✔ cleaned and overwritten: {path.name}")
    else:
        doc.close()
        print(f"   – no changes: {path.name}")


def main():
    folder = Path(input("Folder containing PDFs → ").strip())
    if not folder.is_dir():
        print(f"❌ “{folder}” is not a valid folder.")
        return

    for pdf in sorted(folder.glob("*.pdf")):
        print(f"→ Processing {pdf.name}")
        process_pdf(pdf)

    print("✅ All done.")

if __name__ == "__main__":
    main()
