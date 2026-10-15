from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pymupdf as fitz
import process_pdfs as workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def make_pdf(self, name='input.pdf', title='Mass of the Dead'):
        path = self.root / name
        with fitz.open() as doc:
            for _ in range(2):
                page = doc.new_page()
                page.insert_text((40, 40), title)
                page.insert_text((40, 70), 'Body text remains')
                page.insert_text((40, 780), workflow.BRANDING[0], fontsize=8)
                page.insert_text((40, 795), workflow.BRANDING[1], fontsize=8)
            image = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 20, 20), False)
            image.clear_with(0)
            doc[-1].insert_image(fitz.Rect(30, 700, 70, 740), pixmap=image)
            doc.save(path)
        return path

    def test_complete_workflow_and_repeat(self):
        original = self.make_pdf()
        result = workflow.process_pdf(original)
        self.assertEqual(result.name, 'Mass of the Dead.pdf')
        self.assertFalse(original.exists())
        for _ in range(2):
            with fitz.open(result) as doc:
                self.assertEqual(len(doc), 2)
                for page in doc:
                    text = page.get_text()
                    self.assertIn('Body text remains', text)
                    self.assertNotIn(workflow.BRANDING[0], text)
                    self.assertNotIn(workflow.BRANDING[1], text)
                    self.assertEqual(text.count(workflow.FOOTER), 1)
                self.assertFalse([b for b in doc[-1].get_text('dict')['blocks'] if b['type'] == 1])
            result = workflow.process_pdf(result)

    def test_collision_preserves_existing_pdf(self):
        existing = self.make_pdf('Mass of the Dead.pdf')
        contents = existing.read_bytes()
        result = workflow.process_pdf(self.make_pdf())
        self.assertEqual(result.name, 'Mass of the Dead (1).pdf')
        self.assertEqual(existing.read_bytes(), contents)

    def test_save_failure_preserves_original(self):
        source = self.make_pdf()
        contents = source.read_bytes()
        with patch.object(fitz.Document, 'save', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                workflow.process_pdf(source)
        self.assertEqual(source.read_bytes(), contents)
        self.assertEqual(list(self.root.glob('.mlm-*')), [])

    def test_folder_discovery_and_quoted_path(self):
        source = self.make_pdf('Uppercase.PDF')
        (self.root / 'nested').mkdir()
        (self.root / 'notes.txt').write_text('ignore')
        self.make_pdf('nested/hidden.pdf')
        self.assertEqual(workflow.discover(self.root), [source])
        self.assertEqual(workflow.parse_path(f'"{source}"'), source.resolve())

    def test_corrupt_pdf_does_not_stop_batch(self):
        source = self.make_pdf()
        bad = self.root / 'bad.pdf'
        bad.write_bytes(b'not a PDF')
        with patch('sys.argv', ['process_pdfs.py', str(self.root)]):
            self.assertEqual(workflow.main(), 1)
        self.assertEqual(bad.read_bytes(), b'not a PDF')
        self.assertFalse(source.exists())
        self.assertTrue((self.root / 'Mass of the Dead.pdf').exists())


if __name__ == '__main__':
    unittest.main()
