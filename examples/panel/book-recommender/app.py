"""
Chat application for recommending books to the user.

Input:
Users can submit queries that describe the type of books they are looking for, e.g., suggest fiction novels.
Users can also ask the chat assistant for books by specific author, e.g., recommend books by Dan Brown.
Answers to user's queries will be based on the Goodreads dataset:
https://www.kaggle.com/datasets/cristaliss/ultimate-book-collection-top-100-books-up-to-2023

Application logic:
The app determines the closest matches by comparing user query's embedding to the available
book embeddings. Embeddings of books are pre-computed on the description column of every book
and stored in the assets/ folder.

Response:
The chat assistant then determines the top relevant answers shortlisted by comparing embeddings and
provides the top 5 recommendations.
"""

import json
import panel as pn
from openai import OpenAI
from scipy.spatial import KDTree
import numpy as np
from pathlib import Path
from _wandb import WeightsBiasesTracking
import datetime

from util import get_embedding_from_text

WEIGHTS_AND_BIASES_TRACKING = False

if WEIGHTS_AND_BIASES_TRACKING:
    wandb_client = WeightsBiasesTracking()

with open(Path("assets", "title_to_description.json"), 'r') as file:
    DESCRIPTIONS = json.load(file)

with open(Path("assets", "author_to_title.json"), 'r') as file:
    AUTHOR_TITLES = json.load(file)


def load_embeddings_file():
    """Load the pre-computed embeddings of description column
    The data is in the format title: embedding
    """
    file_path = Path('assets', 'embeddings.json')
    with open(file_path, "r", encoding="utf-8") as file:
        embeddings_json = json.load(file)
    return embeddings_json

client = OpenAI()

pn.extension()


def get_book_description_by_title(title):
    """Return description of a book"""
    return DESCRIPTIONS[title.upper()]


def detect_author(user_query):
    system_prompt = f"""
    You're a system that determines the author in user query. 
    
    You need to return only the author name.Please fix any typo if possible
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What are some books by Sandra Boynton"},
            {"role": "system", "content": "Sandra Boynton"},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )
    author = response.choices[0].message.content.upper()
    return author if author in AUTHOR_TITLES else ""


def book_recommender_agent(user_query, verbose=False, tracking=False):
    """An agent that can recommend books to the user based on input"""
    embeddings_json = load_embeddings_file()

    # If author is mentioned, filter books written by the author.
    # Otherwise, consider all the available books.
    author = detect_author(user_query)
    titles = []
    if author:
        titles = AUTHOR_TITLES[author]
        if verbose:
            print(f"Found these titles: {titles} by author: {author}")

    filtered_embeddings_by_title = {}
    for title in titles:
        title_embedding = embeddings_json.get(title, None)
        if title_embedding:
            filtered_embeddings_by_title[title] = title_embedding
    if filtered_embeddings_by_title:
        embeddings_json = filtered_embeddings_by_title

    titles = []
    embeddings = []
    for key, value in embeddings_json.items():
        if value:
            titles.append(key)
            embeddings.append(value)
    kdtree = KDTree(np.array(embeddings))
    _, indexes = kdtree.query(get_embedding_from_text(user_query), k=min(len(titles), 5))

    if isinstance(indexes, np.int64):
        indexes = [indexes]
    titles_relevant = [titles[i] for i in indexes if titles[i] != "null"]
    if verbose:
        print(f"Found these relevant titles: {titles_relevant}")
    descriptions_relevant = [get_book_description_by_title(title) for title in titles_relevant]

    recommendation_text = ""
    for i, value in enumerate(titles_relevant):
        recommendation_text = f"{recommendation_text}{value}: {descriptions_relevant[i]}\n\n##"

    system_prompt = f"""
You are a helpful book recommendation system that can recommend users books based on their inputs.

Here are the top relevant titles and descriptions (separated by ##) in the format titles: descriptions, 
use these to generate your answer,
and disregard books that are not relevant to user's input. You can display 5 or less recommendations.:

{recommendation_text}

You should also create a summary of the description and format the answer properly. 
You can display a maximum of 5 recommendations.
Please do not suggest any books outside this list.
"""

    if verbose:
        print(f"System prompt: {system_prompt}")

    start_time_ms = datetime.datetime.now().timestamp() * 1000

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )

    end_time_ms = round(datetime.datetime.now().timestamp() * 1000)

    if tracking:
        wandb_client.create_trace(system_prompt, response, user_query, start_time_ms, end_time_ms)

    return response.choices[0].message.content


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    return book_recommender_agent(contents, tracking=WEIGHTS_AND_BIASES_TRACKING)


chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "I am a book recommendation engine! "
    "You may ask questions like: \n* Recommend books by Dan Brown.\n"
    "* Suggest some books based in the Victorian era.\n\n"
    "You can deploy your own by signing up at https://ploomber.io",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="Book Recommender",
    main=[chat_interface],
).servable()
