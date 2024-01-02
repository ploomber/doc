# Python code to convert video to audio
import moviepy.editor as mp
from pathlib import Path
from dotenv import load_dotenv
import os

from haystack import Pipeline
from haystack.components.audio import RemoteWhisperTranscriber
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from elasticsearch_haystack.document_store import ElasticsearchDocumentStore

from pydub import AudioSegment
import math

def chunk_audio(file_path, chunk_length_ms, output_path):
    audio = AudioSegment.from_file(file_path)
    chunk_length = len(audio)
    num_chunks = math.ceil(chunk_length / chunk_length_ms)
    for i in range(0, num_chunks):
        start = i * chunk_length_ms
        end = start + chunk_length_ms
        chunk = audio[start:end]
        chunk.export(f"./{output_path}/chunk_{i}.mp3", format="mp3")

# Usage
load_dotenv(".env")
openaikey = os.getenv("OPENAI")

print("Transforming video to audio...")
# Insert Local Video File Path
file_name = "How_to_Save_Money_Make_6_Figures_as_a_Physical_Therapist.mov"
path_to_video = f"./movie_files/{file_name}"
path_to_audio = f"./audio_files/{file_name.split('.')[0]}.mp3"

# Generate Video File Clip
clip = mp.VideoFileClip(path_to_video)

# Generate Audio File
clip.audio.write_audiofile(path_to_audio)

print("Chunking audio...")
# Chunk audio file
chunk_audio(path_to_audio, 180000, "./chunked_audio")

print("Initializing indexing pipeline...")
# Build indexing pipeline
document_store = ElasticsearchDocumentStore(hosts= "http://localhost:9200/")

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
audio_files = [str(f) for f in Path("./chunked_audio").iterdir() if f.suffix.lower() in ['.mp3']]
p.run({"transcriber": {"sources": audio_files[0:2]}})
