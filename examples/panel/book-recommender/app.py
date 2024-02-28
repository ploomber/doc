"""
Demonstrates how to use the `ChatInterface` and a `callback` function to respond.

The chatbot Assistant echoes back the message entered by the User.

https://github.com/holoviz-topics/panel-chat-examples/blob/main/docs/examples/basics/basic_chat.py
"""

import panel as pn
from openai import OpenAI
from scipy.spatial import KDTree
import numpy as np

from rag_book_recommender import get_book_description_by_title, EmbeddingsStore, get_authors, get_embeddings


client = OpenAI()

pn.extension()

store = EmbeddingsStore()
all_authors = get_authors()


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
    return author if author in all_authors else ""


def book_recommender_agent(user_query, verbose=True):
    """An agent that can retrieve news by topic and summarizes them"""
    # determine the topic based on the query
    embeddings_json = get_embeddings()
    author = detect_author(user_query)
    titles = []
    if author:
        titles = all_authors[author]
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
    _, indexes = kdtree.query(store.get_one(user_query), k=min(len(titles), 3))

    titles_relevant = [titles[i] for i in indexes if titles[i]!="null"]
    print(titles_relevant)
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

You should also create a summary of the description and format the answer properly. 
You can display a maximum of 5 recommendations.
If only 2 relevant texts are found please display those 2 only.
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


chat_interface = pn.chat.ChatInterface(callback=callback, callback_exception='verbose')
chat_interface.send(
    "I am a book recommendation engine! "
    "You may ask questions like: Recommend books by Dan Brown; Suggest some books based in the Victorian era"
    "You can deploy your own by signing up at https://ploomber.io",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="Book Recommender",
    main=[chat_interface],
).servable()
