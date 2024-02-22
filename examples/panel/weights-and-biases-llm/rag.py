
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import MarkdownToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter

from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.readers import ExtractiveReader
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from dotenv import load_dotenv
import os

import requests

load_dotenv(".env")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

def run_indexing_pipeline(url):

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        readme_data = response.json()
        # Fetch the raw README content using the download_url from the README metadata
        
        document_store = InMemoryDocumentStore()
        fetcher = LinkContentFetcher()
        converter = MarkdownToDocument()
        cleaner = DocumentCleaner()
        splitter = DocumentSplitter(split_by="sentence", split_length=100)
        writer = DocumentWriter(document_store = document_store)

        indexing_pipeline = Pipeline()
        indexing_pipeline.add_component(instance=fetcher, name="fetcher")
        indexing_pipeline.add_component(instance=converter, name="converter")
        indexing_pipeline.add_component(instance=cleaner, name="cleaner")
        indexing_pipeline.add_component(instance=splitter, name="splitter")
        indexing_pipeline.add_component(instance=writer, name="writer")

        indexing_pipeline.connect("fetcher.streams", "converter.sources")
        indexing_pipeline.connect("converter.documents", "cleaner.documents")
        indexing_pipeline.connect("cleaner.documents", "splitter.documents")
        indexing_pipeline.connect("splitter.documents", "writer.documents")

        indexing_pipeline.run(data={"fetcher": {"urls": [readme_data['download_url']]}})

        return document_store
    
def run_retrieval_pipeline(document_store, query):
    template = """
    Given the following information, answer the question.

    Context:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}

    Question: {{question}}
    Answer:
    """

    
    generator = OpenAIGenerator()

    prompt_builder = PromptBuilder(template=template)

    retriever = InMemoryBM25Retriever(document_store=document_store)
    reader = ExtractiveReader()
    reader.warm_up()

    basic_rag_pipeline = Pipeline()
    # Add components to your pipeline
    basic_rag_pipeline.add_component("retriever", retriever)
    basic_rag_pipeline.add_component("prompt_builder", prompt_builder)
    basic_rag_pipeline.add_component("llm", generator)

    # Now, connect the components to each other
    basic_rag_pipeline.connect("retriever", "prompt_builder.documents")
    basic_rag_pipeline.connect("prompt_builder", "llm")

    

    response = basic_rag_pipeline.run({"retriever": {"query": query}, "prompt_builder": {"question": query}})

    return response["llm"]["replies"][0]