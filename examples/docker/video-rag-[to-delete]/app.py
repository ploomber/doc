from pathlib import Path
from dataclasses import dataclass

import solara

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import GPTGenerator
from elasticsearch_haystack.embedding_retriever import ElasticsearchEmbeddingRetriever
from elasticsearch_haystack.document_store import ElasticsearchDocumentStore
from dotenv import load_dotenv
import os

load_dotenv(".env")
openaikey = os.getenv("OPENAI")
elastic_search_cloud_id = os.getenv("elastic_search_cloud_id")
elastic_search_host = os.getenv("elastic_search_host")
elastic_username = os.getenv("elastic_username")
elastic_password = os.getenv("elastic_password")
#
# Build RAG pipeline
print("Initializing QA pipeline")
prompt_template = """\
Use the following context to answer the user's question in a friendly manner. \
    If the context provided doesn't answer the question - \
        please respond with: "There is no information in my knowledge base about this".

### CONTEXT
{% for doc in documents %}
  {{ doc.content }}
{% endfor %}

### USER QUESTION
{{query}}
"""

#document_store = ElasticsearchDocumentStore(hosts= "http://localhost:9200/")
document_store = ElasticsearchDocumentStore(hosts=elastic_search_host,
                                            basic_auth=(elastic_username, elastic_password))

prompt_builder = PromptBuilder(prompt_template)
############################################
query_embedder = SentenceTransformersTextEmbedder()
retriever = ElasticsearchEmbeddingRetriever(document_store=document_store)
llm = GPTGenerator(api_key=openaikey)

pipeline = Pipeline()
pipeline.add_component(instance=query_embedder, name="query_embedder")
pipeline.add_component(instance=retriever, name="retriever")
pipeline.add_component(instance=prompt_builder, name="prompt_builder")
pipeline.add_component(instance=llm, name="llm")

pipeline.connect("query_embedder.embedding", "retriever.query_embedding")
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")

###########################################
# Solara app

class State:
    input = solara.reactive("")

css = """
    .main {
        width: 100%;
        height: 100%;
        max-width: 1200px;
        margin: auto;
        padding: 1em;
    }
    
    #app > div > div:nth-child(2) > div:nth-child(2) {
    display: none;
}
"""

chatbox_css = """
.message {
    max-width: 450px;
    width: 100%;
}

.user-message, .user-message > * {
    background-color: #f0f0f0 !important;
}

.assistant-message, .assistant-message > * {
    background-color: #9ab2e9 !important;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid transparent;
  overflow: hidden;
  display: flex;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
"""


@dataclass
class Message:
    role: str
    content: str


def ChatBox(message: Message) -> None:
    solara.Style(chatbox_css)

    align = "start" if message.role == "assistant" else "end"
    with solara.Column(align=align):
        with solara.Card(classes=["message", f"{message.role}-message"]):
            if message.content:
                with solara.Card():
                    solara.Markdown(message.content)
            

        # Image reference: https://www.flaticon.com/free-icons/bot;
        #                  https://www.flaticon.com/free-icons/use

        with solara.HBox(align_items="center"):
            image_path = Path(f"static/{message.role}-logo.png")
            solara.Image(str(image_path), classes=["avatar"])
            solara.Text(message.role.capitalize())

@solara.component
def Chat() -> None:
    solara.Style(
        """
        .chat-input {
            max-width: 800px;
        })
    """
    )

    messages, set_messages = solara.use_state(
        [
            Message(
                role="assistant",
                content=f"Welcome. Please post your queries! My knowledge base\
                    has been curated on a small collection of videos from NASA.  \
                    This collection of videos consist of short clips that talk \
                    about the topics: Mars Perseverance Rover.\
                    Sample questions: \n\nWhat is the Mars Perseverance Rover? \
                        What is the Mars Perseverance Rover mission? \
                        Tell me about the helicopter on Mars."
            )
        ]
    )
    input, set_input = solara.use_state("")

    def ask_rag(pipeline):
        try:
            input_text = State.input.value
            _messages = messages + [Message(role="user", content=input_text)]
            set_input("")
            State.input.value = ""
            set_messages(_messages)

            result = pipeline.run(data={"query_embedder": {"text": input_text}, "prompt_builder": {"query": input_text}})
            rag_response = result['llm']['replies'][0]

            set_messages(_messages + [Message(role="assistant", content=rag_response)])

        except Exception as e:
            set_messages(_messages + [Message(role="assistant", content=f"Cannot answer your current question. Please try again {e}")])

    with solara.VBox():
        for message in messages:
            ChatBox(message)

    with solara.Row(justify="center"):
        with solara.HBox(align_items="center", classes=["chat-input"]):
            solara.InputText(label="Query", value=State.input, continuous_update=False)

    if State.input.value:
        ask_rag(pipeline)

@solara.component
def Page():

    with solara.AppBarTitle():
        solara.Text("Deepen your understanding of our video collection through a Q&A AI assistant")

    with solara.Card(title="About", elevation=6, style="background-color: #f5f5f5;"):
        with solara.Row(justify="center"):
            solara.Image(image="static/nasa-logo.svg", width="100")  # Adjust width and height as needed

        solara.Markdown("Ask questions about our curated database of video using advanced AI tools. \n \
                        This database is curated from the following list of videos: \n \
                        https://images.nasa.gov/search?q=nasa%20perseverance%20rover&page=1&media=video&yearStart=2023&yearEnd=2024")
               
    solara.Style(css)
    with solara.VBox(classes=["main"]):
        solara.HTML(
            tag="h3", style="margin: auto;", unsafe_innerHTML="Chat with the assistant to answer questions about the video topics"
        )

        Chat()

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)