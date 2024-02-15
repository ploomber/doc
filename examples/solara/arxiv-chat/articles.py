import arxiv
from pathlib import Path
import json

class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
        self.results = None

    def _search(self, query):
        search = arxiv.Search(
            query=query,
            max_results = 10,
            sort_by = arxiv.SortCriterion.Relevance
        )
        return search
    
    def get_articles_by_cat(self, query):
        query = f"cat:{query}"
        results = self.client.results(self._search(query))
        return list(results)
    
    def get_articles_by_terms(self, query):
        results = self.client.results(self._search(query))
        return list(results)

    def results_to_json(self, results):
        path = Path("./json/articles.json")
        arr = []
        for r in results:
            arr.append({
                "title": r.title,
                "description": r.summary,
                "published": str(r.published),
                "authors": [a.name for a in r.authors],
                "links": r.links[0].href,
                "categories": r.categories,
            })

        with open(path, "w") as articles_json:
            articles_json.write(json.dumps(arr))

    def results_to_array(self, results):
        out = []
        for r in results:
            out.append(f"{r.title}:\n\n\t{r.summary[:500]}")
        return out

    def format_array_results(self, arr):
        return "\n\n##\n\n".join(arr)