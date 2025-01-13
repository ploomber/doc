from gdrive_loader.models import User, Document
from gdrive_loader.credentials import get_valid_credentials
from googleapiclient.discovery import build
import argparse
from sqlalchemy.orm import Session
from gdrive_loader.db import engine
from openai import OpenAI


def compute_embedding(text: str | list[str], return_single: bool = True) -> list[float]:
    client = OpenAI()
    response = client.embeddings.create(input=text, model="text-embedding-3-small")

    if len(response.data) == 1 and return_single:
        return response.data[0].embedding
    else:
        return [d.embedding for d in response.data]


def convert_doc_to_markdown(document):
    """Convert Google Doc content to Markdown format."""
    markdown = ""
    for element in document.get("body").get("content"):
        if "paragraph" in element:
            paragraph = element["paragraph"]

            # Handle heading styles
            style = paragraph.get("paragraphStyle", {}).get(
                "namedStyleType", "NORMAL_TEXT"
            )
            if "HEADING" in style:
                heading_level = int(style[-1])
                prefix = "#" * heading_level + " "
            else:
                prefix = ""

            # Build paragraph text
            text = ""
            for para_element in paragraph.get("elements"):
                if "textRun" in para_element:
                    text_run = para_element["textRun"]
                    content = text_run.get("content", "")

                    # Handle text styling
                    style = text_run.get("textStyle", {})
                    if style.get("bold"):
                        content = f"**{content}**"
                    if style.get("italic"):
                        content = f"*{content}*"

                    text += content

            markdown += prefix + text

            # Add newlines between paragraphs
            if not text.endswith("\n"):
                markdown += "\n"

    return markdown


def load_documents_from_user(email, dry_run=False, limit=None):
    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(email=email).first()

        if not user:
            raise ValueError(f"User {email} not found")

        credentials = get_valid_credentials(user, db_session)

    # Use the credentials to access Google Drive
    drive_service = build("drive", "v3", credentials=credentials)
    docs_service = build("docs", "v1", credentials=credentials)

    # Query for Google Docs files only
    query = "mimeType = 'application/vnd.google-apps.document' and trashed=false"
    page_token = None
    docs = []
    docs_processed = 0

    while True:
        # Get next page of results
        results = (
            drive_service.files()
            .list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            )
            .execute()
        )

        page_docs = results.get("files", [])
        docs.extend(page_docs)

        # Check if we've reached the limit
        if limit and len(docs) >= limit:
            docs = docs[:limit]
            break

        # Get the next page token
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    if not docs:
        print("No Google Docs found.")
        return

    # First get all document contents and convert to markdown
    markdown_docs = []
    for doc in docs:
        print(f"Converting {doc['name']}...")
        document = docs_service.documents().get(documentId=doc["id"]).execute()
        # limiting to 2000 characters to prevent going over the max context of the model
        markdown_content = convert_doc_to_markdown(document)[:2_000]
        markdown_docs.append((doc["id"], doc["name"], markdown_content))

    if dry_run:
        for _, name, _ in markdown_docs:
            print(f"Would process document: {name}")
        return

    # Compute embeddings in batch
    embeddings = compute_embedding([md[2] for md in markdown_docs], return_single=False)

    # Store everything in database
    with Session(engine) as db_session:
        for (drive_id, name, content), embedding in zip(markdown_docs, embeddings):
            # Check if document already exists
            existing_doc = (
                db_session.query(Document).filter_by(google_drive_id=drive_id).first()
            )

            if existing_doc:
                # Update existing document
                existing_doc.name = name
                existing_doc.content = content
                existing_doc.embedding = embedding
                print(f"Updated document: {name}")

            else:
                # Create new document
                db_doc = Document(
                    name=name,
                    content=content,
                    embedding=embedding,
                    google_drive_id=drive_id,
                    user_id=user.id,
                )
                db_session.add(db_doc)
                print(f"Saved new document: {name}")

        db_session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", type=str, required=True)
    parser.add_argument(
        "--dry-run", action="store_true", help="Print files without storing in DB"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of documents to process",
        default=20,
    )
    args = parser.parse_args()
    load_documents_from_user(args.email, dry_run=args.dry_run, limit=args.limit)
