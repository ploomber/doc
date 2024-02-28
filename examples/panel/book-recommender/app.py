"""
Demonstrates how to use the `ChatInterface` and a `callback` function to respond.

The chatbot Assistant echoes back the message entered by the User.

https://github.com/holoviz-topics/panel-chat-examples/blob/main/docs/examples/basics/basic_chat.py
"""
import json
import panel as pn
from openai import OpenAI
from gnews import GNews
from scipy.spatial import KDTree
import numpy as np
import pickle

from rag_book_recommender import get_book_description_by_title, EmbeddingsStore


client = OpenAI()
google_news = GNews()

pn.extension()


store = EmbeddingsStore()

with open("genres.pkl", 'rb') as file:
    GENRES = pickle.load(file)

with open("author_to_title.pkl", 'rb') as file:
    AUTHORS = pickle.load(file)


def genre_classifier(user_query):
    genres_ = ", ".join(GENRES)
    system_prompt = f"""
    You're a system that determines the book genre in user's query.

    You must classify a user prompt into a comma separated list of top 5 genres wheres available genres are:

{genres_[:100]}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Recommend some thriller books?"},
            {"role": "system", "content": "THRILLER"},
            {"role": "user", "content": "I want a list of fictional books"},
            {"role": "system", "content": "FICTION,SCIENCE FICTION,SCIENCE FICTION FANTASY,"
                                          "HISTORICAL FICTION,LITERARY FICTION"},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )
    genre_list = response.choices[0].message.content.split(",")
    valid_genres = [genre for genre in genre_list if genre.upper() in GENRES]
    return ", ".join(valid_genres)


def detect_author(user_query):
    system_prompt = f"""
    You're a system that determines the author in user query. 
    
    You need to return only he author name.Please fix any typo if possible
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
    return author if author in AUTHORS else ""


def book_recommender_agent(user_query, verbose=True):
    """An agent that can retrieve news by topic and summarizes them"""
    # determine the topic based on the query
    genre = genre_classifier(user_query)

    author = detect_author(user_query)
    titles = []
    if author:
        titles = AUTHORS[author]
        if verbose:
            print(f"Found these titles: {titles} by author: {author}")

    if verbose:
        print(f"Genre: {genre}")

    with open("embeddings.json", "r", encoding="utf-8") as file:
        embeddings_json = json.load(file)

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
    _, indexes = kdtree.query(store.get_one(user_query), k=min(len(titles), 3))

    titles_relevant = [titles[i] for i in indexes]
    descriptions_relevant = [get_book_description_by_title(title) for title in titles_relevant]

    recommendation_text = ""
    for i, value in enumerate(titles_relevant):
        recommendation_text = f"{recommendation_text}{value}: {descriptions_relevant[i]}\n\n##"

    system_prompt = f"""
You are a helpful book recommendation system that can recommend users books based on their inputs.

Here are the top relevant titles and descriptions (separated by ##) in the format titles: descriptions, 
use these to generate your answer,
and disregard books that are not relevant to user's input:

{recommendation_text}

You should also create a summary of the description and format the answer properly. Select upto 5 recommendations.
Please do not suggest any books outside this list.
"""

    if verbose:
        print(f"System prompt: {system_prompt}")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )

    return response.choices[0].message.content


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    return book_recommender_agent(contents)


chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "I am a book recommendation engine! You can deploy your own by signing up at https://ploomber.io",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="Book Recommender",
    main=[chat_interface],
).servable()