from dotenv import load_dotenv
import os 

import openai
import solara
import solara.lab
from solara.components.file_drop import FileDrop

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import GPTGenerator
from elasticsearch_haystack.embedding_retriever import ElasticsearchEmbeddingRetriever
from elasticsearch_haystack.document_store import ElasticsearchDocumentStore

from chat import chatbox_css, Message, ChatBox

load_dotenv(".env")
openaikey = os.getenv("OPENAI")
qdrant = os.getenv("qdrant")
elastic_search_host = os.getenv("elastic_search_host")
elastic_username = os.getenv("elastic_username")
elastic_password = os.getenv("elastic_password")

# Build RAG pipeline
print("Initializing QA pipeline")
######## Complete this section #############
prompt_template = """\
Use the following context to answer the user's question in a friendly manner. \
    If the context provided doesn't answer the question - \
        please respond with: "I don't know".

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

openai.api_key = os.getenv("OPENAI")

pipeline.draw("question_answer_pipeline.png")

class State:
    video_data = solara.reactive(None)
    video_upload_error = solara.reactive("")
    existing_video_selection = solara.reactive("")
    input = solara.reactive("")

    @staticmethod
    def select_existing_video(video_name):
        # Assuming video_name is the name or path of the pre-existing video
        State.existing_video_selection.value = video_name
        State.video_data.value = None
        State.video_upload_error.value = ""

    @staticmethod
    def load_from_file(file):
        allowed_extensions = ['.mp4', '.avi', '.mov']
        if not any(file["name"].lower().endswith(ext) for ext in allowed_extensions):
            State.video_upload_error.value = "Only MP4, AVI, MOV files are supported"
            return
        try:
            # Assuming file is a video file, process as needed
            State.video_data.value = file
            # Add any additional processing you need for the video file here
        except Exception as e:
            State.video_upload_error.value = str(e)

        try:
            # Process the video file
            video_path = State.save_temp_video(file)
            audio_path = State.convert_video_to_audio(video_path)
            chunked_audio_paths = State.chunk_audio(audio_path, 180000)  # Chunk length in ms

            # Run the indexing pipeline
            State.index_audio_chunks(chunked_audio_paths)
        except Exception as e:
            State.video_upload_error.value = str(e)


    @staticmethod
    def reset():
        State.video_data.value = None
        State.video_upload_error.value = ""
    

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
                content=f"Welcome. Please post your queries!"
            )
        ]
    )
    input, set_input = solara.use_state("")

    def ask_rag():
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
            set_messages(_messages + [Message(role="assistant", content=str(e))])

    with solara.VBox():
        for message in messages:
            ChatBox(message)

    with solara.Row(justify="center"):
        with solara.HBox(align_items="center", classes=["chat-input"]):
            solara.InputText(label="Query", value=State.input, continuous_update=False)

    if State.input.value:
        ask_rag()



@solara.component
def Page():

    video_upload_error = State.video_upload_error.value
    existing_videos = ["video1.mp4", "video2.mov"]  # List of pre-existing videos

    with solara.AppBarTitle():
        solara.Text("Video Upload and Analysis App")

    with solara.Card(title="About", elevation=6, style="background-color: #f5f5f5;"):
        solara.Markdown("Upload and analyze video content using advanced AI tools.")

    with solara.Sidebar():
        with solara.Card("Controls", margin=0, elevation=0):
            with solara.Column():
                FileDrop(
                    on_file=State.load_from_file,
                    on_total_progress=lambda *args: None,
                    label="Drag a video file here",
                )

                for video in existing_videos:
                    solara.Button(video, on_click=lambda v=video: State.select_existing_video(v))

                if State.existing_video_selection.value:
                    solara.Info(f"Selected video: {State.existing_video_selection.value}")

                if State.video_data.value:
                    solara.Info("Video is successfully uploaded")
                    # Code to display the uploaded video goes here

                if video_upload_error:
                    solara.Error(f"Error uploading video: {video_upload_error}")


    solara.Style(css)
    with solara.VBox(classes=["main"]):
        solara.HTML(
            tag="h3", style="margin: auto;", unsafe_innerHTML="Chat with my video"
        )

        Chat()

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)