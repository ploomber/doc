import  modal

# Create a custom image with ffmpeg installed
ffmpeg_image = modal.Image.debian_slim(python_version="3.11").run_commands(
    "apt-get update",
    "apt-get install -y ffmpeg",
    "pip install haystack-ai elasticsearch-haystack==0.1.2 solara openai python-dotenv pydub moviepy modal pytube",
)

from dotenv import load_dotenv
import os 
from pathlib import Path
from pytube import YouTube

from haystack import Pipeline
from haystack.components.audio import RemoteWhisperTranscriber
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from elasticsearch_haystack.document_store import ElasticsearchDocumentStore

import moviepy.editor as mp
from pathlib import Path

from pydub import AudioSegment
import math

from youtube_dl import YoutubeDL


stub = modal.Stub()

volume = modal.Volume.persisted("my-video-volume")

# Usage
load_dotenv("../.env")
openaikey = os.getenv("OPENAI")
elastic_search_cloud_id = os.getenv("elastic_search_cloud_id")
elastic_search_host = os.getenv("elastic_search_host")
elastic_username = os.getenv("elastic_username")
elastic_password = os.getenv("elastic_password")

def create_directories():
    Path("./movie_files").mkdir(parents=True, exist_ok=True)
    Path("./audio_files").mkdir(parents=True, exist_ok=True)
    Path("./chunked_audio").mkdir(parents=True, exist_ok=True)


def download_audio(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    path_to_video = "temp_audio"
    out_file = video.download(output_path=path_to_video)
    base, ext = os.path.splitext(out_file)

     # Generate Video File Clip
    clip = mp.VideoFileClip(path_to_video)

    # Generate Audio File
    clip.audio.write_audiofile(path_to_audio)

def chunk_audio(file_path, chunk_length_ms, output_path):
    audio = AudioSegment.from_file(file_path)
    chunk_length = len(audio)
    num_chunks = math.ceil(chunk_length / chunk_length_ms)
    for i in range(0, num_chunks):
        start = i * chunk_length_ms
        end = start + chunk_length_ms
        chunk = audio[start:end]
        chunk.export(f"./{output_path}/chunk_{i}.mp3", format="mp3")

def convert_video_to_audio(youtube_link="https://www.youtube.com/watch?v=X5EynjBZRZo&pp=ygUPc2NpZW5jZSBwb2RjYXN0"):
    download_audio(url)

    # make a directory under chunked_audio with the file_name as the folder name
    file_name = f"{youtube_link.split('=')[-1]}"
    path_to_audio = f"./audio_files/{file_name}.mp3"
    Path(f"./chunked_audio/{path_to_audio}").mkdir(parents=True, exist_ok=True)


    print("Chunking audio...")
    # Chunk audio file
    chunk_audio(path_to_audio, 180000, f"./chunked_audio/{file_name}")


@stub.function(volumes={"/data": volume}, image=ffmpeg_image)
def process_video(video_path: str):
    create_directories()
    convert_video_to_audio(video_path)
    document_store = ElasticsearchDocumentStore(hosts=elastic_search_host,
                                            basic_auth=(elastic_username, elastic_password))

    embedder = SentenceTransformersDocumentEmbedder()
    transcriber = RemoteWhisperTranscriber(api_key=openaikey)
    documentcleaner = DocumentCleaner()
    splitter = DocumentSplitter(split_by="sentence", 
                                split_length=10)
    p = Pipeline()
    p.add_component(instance=transcriber, name="transcriber")
    p.add_component(instance=documentcleaner, name="cleaner")
    p.add_component(instance= splitter, name="splitter")
    p.add_component(instance=embedder, name="embedder")
    p.add_component(instance=DocumentWriter(document_store=document_store), name="writer")

    p.connect("transcriber.documents", "cleaner.documents")
    p.connect("cleaner.documents", "splitter.documents")
    p.connect("splitter.documents", "embedder.documents")
    p.connect("embedder.documents", "writer.documents")
    p.draw("./images/indexing_pipeline.png")
    audio_files = [str(f) for f in Path("./chunked_audio").rglob("*.mp3")]
    p.run({"transcriber": {"sources": audio_files}})

@stub.local_entrypoint()
def main():
    process_video.remote("https://www.youtube.com/watch?v=mG3EOg02NUg&pp=ygUPc2NpZW5jZSBwb2RjYXN0")