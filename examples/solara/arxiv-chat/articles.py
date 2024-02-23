import arxiv
from pathlib import Path
import json
import fitz
import tiktoken

MAX_CHUNK_SIZE = 1500 # measured in tokens



class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def token_length(self, text):
        return len(self.encoding.encode(text))

    def _search(self, query, criterion="relevance", order="descending"):
        criterion_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate,
        }
        order_map = {
            "ascending": arxiv.SortOrder.Ascending,
            "descending": arxiv.SortOrder.Descending,
        }
        search = arxiv.Search(
            query=query,
            max_results=10,
            sort_by=criterion_map[criterion],
            sort_order=order_map[order]
        )
        # print(f"Searching: {query}\nOrder by: {criterion} {order}")
        return search
    
    def _search_by_id(self, id):
        return list(self.client.results(arxiv.Search(
            id_list=[id]
        )))[0]
    
    def download_article(self, id=None):
        result = self._search_by_id(id)
        info = {
            "id": result.get_short_id(),
            "title": result.title,
            "description": result.summary,
            "published": str(result.published),
            "authors": [a.name for a in result.authors],
            "links": result.links[0].href,
            "categories": result.categories,
        }

        result.download_pdf(filename="article.pdf")

        doc = fitz.open("article.pdf")
        # out = open("output.txt", "wb")

        print(f"Document length: {len(doc)}")
        chunks = []
        curr_chunk = ""

        for p in doc:
            t = p.get_text()
            # out.write(t.encode("utf8")) # write text of pag
            length = self.token_length(curr_chunk)
            if length + self.token_length(t) <= MAX_CHUNK_SIZE:
                curr_chunk += t
            else:
                # print(f"Length: {self.token_length(curr_chunk)}, Chunk: {curr_chunk[:15]}")
                chunks.append(curr_chunk)
                curr_chunk = t

        Path("article.pdf").unlink()
        # out.close()
        print("Downloaded file.")
        return info, chunks
    
    def get_articles_by_cat(self, query):
        query = f"cat:{query}"
        results = self.client.results(self._search(query))
        return list(results)
    

    def get_articles_by_terms(self, query, criterion="relevance", order="descending"):
        results = self.client.results(self._search(query, criterion, order))
        return list(results)

    def results_to_json(self, results):
        path = Path("./json/articles.json")
        arr = []
        for r in results:
            arr.append({
                "id": r.get_short_id(),
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