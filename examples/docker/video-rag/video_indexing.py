# Python code to convert video to audio
import moviepy.editor as mp
from pathlib import Path

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

def convert_video_to_audio(file_name):
    path_to_video = f"./movie_files/{file_name}"
    path_to_audio = f"./audio_files/{file_name.split('.')[0]}.mp3"


    print("Transforming video to audio...")

    # Generate Video File Clip
    clip = mp.VideoFileClip(path_to_video)

    # Generate Audio File
    clip.audio.write_audiofile(path_to_audio)

    # make a directory under chunked_audio with the file_name as the folder name
    Path(f"./chunked_audio/{file_name.split('.')[0]}").mkdir(parents=True, exist_ok=True)


    print("Chunking audio...")
    # Chunk audio file
    chunk_audio(path_to_audio, 180000, f"./chunked_audio/{file_name.split('.')[0]}")

