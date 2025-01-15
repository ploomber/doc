from celery import Celery
from pdf_loader import SETTINGS
from pdf_loader.models import Document, DocumentStatus
from pdf_loader.db import engine
from sqlalchemy.orm import Session
from pdf_loader.embedding import compute_embedding
from pathlib import Path
import easyocr
import fitz  # PyMuPDF

app = Celery("pdf_loader.background", broker="amqp://localhost")
app.conf.broker_connection_retry_on_startup = True


@app.task
def process_pdf_document(filename: str):
    with Session(engine) as db_session:
        document = db_session.query(Document).filter(Document.name == filename).first()
        if not document:
            return

        document.status = DocumentStatus.PROCESSING
        db_session.commit()

        content = pdf_ocr(filename)

        # to prevent going over the max length
        embedding = compute_embedding(content[:5000])
        document.content = content
        document.embedding = embedding
        document.status = DocumentStatus.COMPLETED
        db_session.commit()


def pdf_ocr(filename: str) -> str:
    content = Path(SETTINGS.PATH_TO_UPLOADS / filename).read_bytes()

    # Initialize OCR reader
    reader = easyocr.Reader(["en"])

    # Load PDF from bytes
    pdf = fitz.open(stream=content, filetype="pdf")

    extracted_text = []

    # Process each page
    for page in pdf:
        # Convert page to image
        pix = page.get_pixmap()
        img_bytes = pix.tobytes()

        # Run OCR
        results = reader.readtext(img_bytes)

        # Extract text from results
        page_text = " ".join([text[1] for text in results])
        extracted_text.append(page_text)

    return "\n\n".join(extracted_text)


if __name__ == "__main__":
    # this will force a model download
    easyocr.Reader(["en"])
