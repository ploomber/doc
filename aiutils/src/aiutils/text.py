from PIL import Image
import pytesseract
import fitz


def image2text(path_to_image):
    """Extracts text from a single image"""
    return pytesseract.image_to_string(Image.open(path_to_image))


def pdf2text(path_to_pdf):
    """Extracts text from a single PDF file"""
    doc = fitz.open(path_to_pdf)
    return [page.get_text() for page in doc]
