#!/usr/bin/env python3
"""Clean, brand, and rename a PDF or a folder of PDFs in place."""
import argparse
import os
from pathlib import Path
import re
import shlex
import stat
import tempfile

import pymupdf as fitz

BRANDING = (
    "INSTITUTE OF CHRIST THE KING SOVEREIGN PRIEST",
    "www.institute-christ-king.org",
    "WWW.MYLATINMASS.COM",
)
FOOTER = "WWW.MYLATINMASS.COM"


def parse_path(value):
    value = value.strip()
    if not Path(value).expanduser().exists():
        try:
            parts = shlex.split(value)
            if len(parts) == 1:
                value = parts[0]
        except ValueError:
            pass
    return Path(value).expanduser().resolve()


def discover(path):
    if path.is_file() and path.suffix.lower() == ".pdf":
        return [path]
    if path.is_dir():
        return sorted((p for p in path.iterdir()
                       if p.is_file() and not p.is_symlink()
                       and p.suffix.lower() == ".pdf"), key=lambda p: p.name.lower())
    raise ValueError("Enter an existing folder or a PDF file.")


def target_path(source, title):
    title = re.sub(r'[\\/:"*?<>|\x00-\x1f]', '', title)
    title = re.sub(r'\s+', ' ', title).strip(' .')
    # Leave room for extension and collision suffixes on common filesystems.
    while len(title.encode('utf-8')) > 200:
        title = title[:-1]
    if not title:
        return source
    target = source.with_name(title + '.pdf')
    number = 1
    while target.exists() and target != source:
        target = source.with_name(f'{title} ({number}).pdf')
        number += 1
    return target


def process_pdf(source):
    temporary = None
    try:
        with fitz.open(source) as doc:
            if doc.needs_pass:
                raise ValueError('Password-protected PDF; skipped.')
            if not len(doc):
                raise ValueError('PDF has no pages; skipped.')
            # Capture title before inserting our own footer.
            title = next((line.strip() for line in doc[0].get_text().splitlines()
                          if line.strip() and line.strip() not in BRANDING), '')
            target = target_path(source, title)
            for page in doc:
                redactions = []
                for text in BRANDING:
                    redactions.extend(page.search_for(text))
                if page.number == len(doc) - 1:
                    for block in page.get_text('dict')['blocks']:
                        if block['type'] == 1 and block['bbox'][1] > page.rect.height * .8:
                            redactions.append(fitz.Rect(block['bbox']))
                for rect in redactions:
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                if redactions:
                    page.apply_redactions(
                        images=fitz.PDF_REDACT_IMAGE_PIXELS,
                        graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                        text=fitz.PDF_REDACT_TEXT_REMOVE,
                    )
                width, height = page.rect.width, page.rect.height
                font_size = min(16, (width - 20) / fitz.get_text_length(FOOTER, fontname='tiro', fontsize=1))
                rect = fitz.Rect(10, height - 36, width - 10, height - 8)
                if font_size <= 0 or page.insert_textbox(
                    rect, FOOTER, fontname='tiro', fontsize=font_size, align=1
                ) < 0:
                    raise ValueError('Page is too small for the website footer.')
            fd, temporary = tempfile.mkstemp(prefix='.mlm-', suffix='.tmp', dir=source.parent)
            os.close(fd)
            doc.save(temporary, garbage=4, deflate=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        with fitz.open(temporary) as check:
            if not len(check):
                raise ValueError('Saved PDF could not be verified.')
        os.chmod(temporary, stat.S_IMODE(source.stat().st_mode))
        os.replace(temporary, target)
        temporary = None
        if target != source:
            source.unlink()
        return target
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', help='PDF file or folder (prompts if omitted)')
    args = parser.parse_args()
    try:
        value = args.path if args.path is not None else input('Folder or PDF path → ')
        if not value.strip():
            raise ValueError('No path supplied.')
        files = discover(parse_path(value))
    except (ValueError, OSError) as error:
        print(f'Error: {error}')
        return 1
    if not files:
        print('No PDF files found in this folder.')
        return 0
    print(f'Processing {len(files)} PDF(s). Originals will be replaced in the same folder.')
    failed = 0
    for source in files:
        try:
            result = process_pdf(source)
            print(f'OK: {source.name} → {result.name}')
        except Exception as error:
            failed += 1
            print(f'FAILED: {source.name}: {error}')
    print(f'Done: {len(files) - failed} succeeded, {failed} failed.')
    return 1 if failed else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled.')
        raise SystemExit(130)
