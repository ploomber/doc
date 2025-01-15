from openai import OpenAI
import mistune
from pdf_loader.models import Document
from sqlalchemy.orm import Session
from pdf_loader.db import engine
from pdf_loader.embedding import compute_embedding


SYSTEM_PROMPT = """
You are a helpful assistant that can answer questions about the documents provided.

Limit your response to the documents provided.

If you cannot find the answer in the documents, say
"The document does not contain the answer".

Respond in markdown format.
"""


def answer_query(query: str) -> str:
    embedding = compute_embedding(query, return_single=True)
    with Session(engine) as db_session:
        similar_docs = Document.find_similar(
            db_session,
            embedding=embedding,
            limit=5,
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": "\n\n".join([doc.content for doc in similar_docs]),
        },
        {
            "role": "user",
            "content": query,
        },
    ]

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return mistune.html(response.choices[0].message.content)
