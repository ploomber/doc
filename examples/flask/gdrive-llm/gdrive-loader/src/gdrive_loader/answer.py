from openai import OpenAI
from gdrive_loader.models import Document, User
from sqlalchemy.orm import Session
from gdrive_loader.db import engine
from gdrive_loader.load import compute_embedding


def answer_query(query: str, email: str) -> str:
    embedding = compute_embedding(query, return_single=True)
    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(email=email).first()
        similar_docs = Document.find_similar(
            db_session,
            embedding=embedding,
            user_id=user.id,
            limit=5,
        )

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that can answer questions about the documents provided.",
            },
            {
                "role": "user",
                "content": "\n\n".join([doc.to_markdown() for doc in similar_docs]),
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    return response.choices[0].message.content
