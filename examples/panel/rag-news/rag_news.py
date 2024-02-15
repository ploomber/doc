import json
from pathlib import Path

from gnews import GNews
from openai import OpenAI

client = OpenAI()

# these are the values that the GNews.get_news_by_topic function can take
TOPICS = {
    "WORLD",
    "NATION",
    "BUSINESS",
    "TECHNOLOGY",
    "ENTERTAINMENT",
    "SPORTS",
    "SCIENCE",
    "HEALTH",
}


class EmbeddingsStore:
    def __init__(self):
        self._path = Path("embeddings.json")

        if not self._path.exists():
            self._data = {}
        else:
            self._data = json.loads(self._path.read_text())

    def get_one(self, text):
        if text in self._data:
            return self._data[text]

        response = client.embeddings.create(input=text, model="text-embedding-3-small")

        embedding = response.data[0].embedding

        self._data[text] = embedding
        self._path.write_text(json.dumps(self._data))

        return embedding

    def get_many(self, content):
        return [self.get_one(text) for text in content]

    def __len__(self):
        return len(self._data)

    def clear(self):
        self._path.unlink()
        self._data = {}


news_dir = Path("news")


def download_news():
    """Download news from GNews for each topic"""

    news_dir.mkdir(exist_ok=True)

    google_news = GNews()

    for topic in TOPICS:
        print(f"Downloading news for {topic}...")
        news = google_news.get_news_by_topic(topic)

        with open(news_dir / f"{topic}.json", "w") as file:
            json.dump(news, file, indent=2)

        print(f"Downloaded {len(news)} news for {topic}")


def get_news_by_topic(topic):
    """Get news from a specific topic"""
    with open(news_dir / f"{topic}.json") as file:
        return json.load(file)


def get_descriptions(news):
    """Get news descriptions from a list of dictionaries, as returned by GNews"""
    return [article["description"] for article in news]


def compute_embeddings():
    store = EmbeddingsStore()
    store.clear()

    for topic in TOPICS:
        news = get_news_by_topic(topic)
        descriptions = get_descriptions(news)
        store.get_many(descriptions)


if __name__ == "__main__":
    # download today's news
    download_news()

    # compute embeddings
    compute_embeddings()
    