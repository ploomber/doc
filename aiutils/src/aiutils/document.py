import tiktoken
import fitz
from PIL import Image
from jinja2 import Template

import aiutils.text
from aiutils import tables


encoding = tiktoken.get_encoding("cl100k_base")


# gpt-3.5-turbo-0125
PRICE_PER_TOKEN = 0.0005 / 1_000


# gpt-4-0125-preview
# PRICE_PER_TOKEN = 0.01 / 1_000


template_page = Template(
    """
### START PAGE {{ page_number }} ###
{{ text }}
### TABLES PAGE {{ page_number }} ###
{{ tables }}
### END PAGE {{ page_number }} ###
"""
)


class Document:
    def __init__(self, path) -> None:
        self._path = path
        self._text_pages = aiutils.text.pdf2text(self._path)
        self._n_tokens = sum([len(encoding.encode(page)) for page in self._text_pages])
        self._n_pages = len(self._text_pages)

    def pages(self):
        for page in self._text_pages:
            yield page

    def get_page_as_image(self, page_number):
        """Return a page as an image"""
        doc = fitz.open(self._path)

        # render at a higher res using matrix to improve ocr
        # https://github.com/pymupdf/PyMuPDF/issues/322#issuecomment-512561756
        pix = doc[page_number].get_pixmap(matrix=fitz.Matrix(2, 2))

        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    def get_tables_in_page(self, page_number):
        """Return a list of tables in the page. Each table is a dictionary"""
        # TODO: make the detectors a singleton to avoid loading the model every time
        table_detector = tables.TableDetector()
        page = self.get_page_as_image(page_number)
        tables_detected = table_detector.detect(page)
        cropped = tables.crop_tables(page, tables_detected)
        detector_structure = tables.TableStructureDetector()
        tables_detected = [detector_structure.detect(img) for img in cropped]
        coords = [tables.get_cell_coordinates_by_row(t[1]) for t in tables_detected]
        out = [tables.apply_ocr(c, img) for c, img in zip(coords, cropped)]

        # TODO: we need to export the tables to a format that can be used in the prompt
        return [table[1] for table in out]

    def iter_tables(self):
        for i in range(self._n_pages):
            tables = self.get_tables_in_page(i)
            yield tables

    def iter_prompts(self):
        """Iterate over the pages and tables and return a prompt for the document"""
        for i, text, tables in zip(
            range(self._n_pages),
            self.pages(),
            self.iter_tables(),
        ):
            yield template_page.render(text=text, tables=tables, page_number=i)

    def __repr__(self) -> str:
        return (
            f"Document(path={self._path}, n_tokens={self._n_tokens:,}, "
            f"price={self._n_tokens * PRICE_PER_TOKEN:.2f} USD)"
        )
