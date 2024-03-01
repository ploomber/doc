from openai import OpenAI

client = OpenAI()


def get_embedding_from_text(text):
    """Generate embedding for a text"""
    try:
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        embedding = response.data[0].embedding
        return embedding
    except Exception:
        return []
