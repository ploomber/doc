import json
import pickle
import pandas as pd
from pathlib import Path
from openai import OpenAI

client = OpenAI()

df = pd.read_csv("goodreads.csv")

with open("title_to_description.pkl", 'rb') as file:
    DESCRIPTIONS = pickle.load(file)


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
            print("Failed")
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


def get_book_description_by_title(title):
    print(title)
    return DESCRIPTIONS[title.upper()]


def compute_embeddings():
    store = EmbeddingsStore()
    store.clear()

    for index, row in df.iterrows():
        print(index)
        store.get_one(row["description"], row["title"])


if __name__ == "__main__":

    # compute embeddings
    compute_embeddings()
