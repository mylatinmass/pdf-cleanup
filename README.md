# My Latin Mass PDF workflow

Requires Python 3.10 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python process_pdfs.py
```

At the prompt, paste a folder path or a single PDF path. Quoted paths and paths dragged from Finder are supported. You can also provide the path directly:

```sh
python process_pdfs.py "/path/to/PDF folder"
python process_pdfs.py "/path/to/file.pdf"
```

For each PDF the workflow:

1. Removes the Institute of Christ the King name and website wherever searchable text matches.
2. Removes image blocks starting below 80% of the last page's height. This is a position-based rule: other artwork in that area is also removed. Scanned full-page images are not recognized as footer images.
3. Adds `WWW.MYLATINMASS.COM` centered on every page, replacing existing searchable copies so reruns do not stack the footer.
4. Renames the PDF using its first nonblank text line (captured before stamping), in the same folder. If no suitable title is found, keeps its filename. Existing files with that title are preserved using numbered filename suffixes.

**This replaces originals. Keep backups if you need the original PDFs.** Each PDF is saved to a temporary file and reopened before replacement. A failed file is reported and processing continues. Folder searches include only immediate files, support `.pdf` and `.PDF`, and skip symbolic links. Password-protected PDFs are skipped. Text removal requires searchable text; this does not perform OCR. The footer needs clear space at the bottom of each page.

The older scripts are retained as standalone utilities; `process_pdfs.py` is the combined workflow.

Run verification with `python -m unittest discover -s tests -v`.
