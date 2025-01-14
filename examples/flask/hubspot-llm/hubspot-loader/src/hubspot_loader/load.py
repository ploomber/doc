from hubspot_loader.models import Document
import argparse
from sqlalchemy.orm import Session
from hubspot_loader.db import engine
from openai import OpenAI
import hubspot
from hubspot_loader import SETTINGS


def compute_embedding(text: str | list[str], return_single: bool = True) -> list[float]:
    client = OpenAI()
    response = client.embeddings.create(input=text, model="text-embedding-3-small")

    if len(response.data) == 1 and return_single:
        return response.data[0].embedding
    else:
        return [d.embedding for d in response.data]


def iter_tickets(after=None, limit=None, _fetched=0):
    client = hubspot.Client.create(access_token=SETTINGS.HUBSPOT_ACCESS_TOKEN)
    api_response = client.crm.tickets.basic_api.get_page(
        # max value is 100
        limit=100,
        archived=False,
        after=after,
    )

    for ticket in api_response.results:
        if limit is not None and _fetched >= limit:
            return
        yield ticket
        _fetched += 1

    if api_response.paging and (limit is None or _fetched < limit):
        yield from iter_tickets(
            api_response.paging.next.after,
            limit=limit,
            _fetched=_fetched,
        )


def load_tickets(limit=None, dry_run=False, reset=False):
    if reset:
        with Session(engine) as db_session:
            db_session.query(Document).delete()
            db_session.commit()

    with Session(engine) as db_session:
        last_token = (
            db_session.query(Document.hubspot_ticket_id)
            .order_by(Document.id.desc())
            .first()
        )
        if last_token:
            after = str(int(last_token[0]) + 1)
        else:
            after = None

    if dry_run:
        for ticket in iter_tickets(limit=limit, after=after):
            print(f"Would process ticket: {ticket.id} - {ticket.properties['subject']}")
        return

    with Session(engine) as db_session:
        batch = []
        batch_contents = []

        for ticket in iter_tickets(limit=limit, after=after):
            document = Document(
                name=ticket.properties["subject"],
                content=ticket.properties["content"],
                hubspot_ticket_id=ticket.id,
            )
            batch.append(document)
            batch_contents.append(document.content)

            if len(batch) == 10:
                embeddings = compute_embedding(batch_contents, return_single=False)
                for doc, emb in zip(batch, embeddings):
                    doc.embedding = emb
                    db_session.add(doc)
                batch = []
                batch_contents = []

        # Handle remaining documents in final batch
        if batch:
            embeddings = compute_embedding(batch_contents, return_single=False)
            for doc, emb in zip(batch, embeddings):
                doc.embedding = emb
                db_session.add(doc)

        db_session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of documents to process",
        default=20,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print tickets that would be processed without storing them",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Fetch all tickets from the start",
        default=False,
    )
    args = parser.parse_args()
    load_tickets(limit=args.limit, dry_run=args.dry_run, reset=args.reset)
