import os
import json
import pickle
import pandas as pd

from pathlib import Path
from openai import OpenAI

client = OpenAI()

file_path = os.path.join('assets', 'goodreads.csv')
df = pd.read_csv(file_path)


file_path = os.path.join('assets', 'title_to_description.pkl')
with open(file_path, 'rb') as file:
    DESCRIPTIONS = pickle.load(file)


def get_authors():
    file_path = os.path.join('assets', 'author_to_title.pkl')
    with open(file_path, 'rb') as file:
        authors = pickle.load(file)
    return authors


def get_embeddings():
    file_path = os.path.join('assets', 'embeddings.json')
    with open(file_path, "r", encoding="utf-8") as file:
        embeddings_json = json.load(file)
    return embeddings_json


def get_book_description_by_title(title):
    return DESCRIPTIONS[title.upper()]


class EmbeddingsStore:
    def __init__(self):
        self._path = Path("embeddings.json")

        if not self._path.exists():
            self._data = {}
        else:
            self._data = json.loads(self._path.read_text())

    def get_one(self, text, title=None):
        if text in self._data:
            return self._data[text]

        try:
            response = client.embeddings.create(input=text, model="text-embedding-3-small")

            embedding = response.data[0].embedding

            self._data[title] = embedding
            self._path.write_text(json.dumps(self._data))

            return embedding
        except Exception:
            self._data[title] = []
            self._path.write_text(json.dumps(self._data))
            return None

    def get_many(self, content, title):
        return [self.get_one(text, title) for text in content]

    def __len__(self):
        return len(self._data)

    def clear(self):
        if self._path.exists():
            self._path.unlink()
            self._data = {}


def compute_embeddings():
    store = EmbeddingsStore()
    store.clear()

    for index, row in df.iterrows():
        print(f"Index: {index}")
        store.get_one(row["description"], row["title"])


if __name__ == "__main__":

    # compute embeddings
    compute_embeddings()
