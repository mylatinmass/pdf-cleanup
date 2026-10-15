# pip install PyMuPDF
import fitz  # PyMuPDF

INPUT_PDF     = "(In Paschal Time).pdf"
OUTPUT_PDF    = "PaschalTime_cleaned.pdf"
FOOTER_TEXT   = "INSTITUTE OF CHRIST THE KING SOVEREIGN PRIEST"
WEBSITE_TEXT  = "www.institute-christ-king.org"

doc = fitz.open(INPUT_PDF)
for page in doc:
    # 1) redact the repeated header/footer string
    for r in page.search_for(FOOTER_TEXT):
        page.add_redact_annot(r, fill=(1,1,1))
    # 2) redact the old website URL
    for r in page.search_for(WEBSITE_TEXT):
        page.add_redact_annot(r, fill=(1,1,1))
    # 3) apply any pending redactions on this page
    if page.first_annot:
        page.apply_redactions()

# 4) save out your cleaned PDF
doc.save(OUTPUT_PDF)
