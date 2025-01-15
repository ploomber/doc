from openai import OpenAI


def compute_embedding(text: str | list[str], return_single: bool = True) -> list[float]:
    client = OpenAI()
    response = client.embeddings.create(input=text, model="text-embedding-3-small")

    if len(response.data) == 1 and return_single:
        return response.data[0].embedding
    else:
        return [d.embedding for d in response.data]
