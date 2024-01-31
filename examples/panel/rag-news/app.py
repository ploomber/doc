"""
Demonstrates how to use the `ChatInterface` and a `callback` function to respond.

The chatbot Assistant echoes back the message entered by the User.

https://github.com/holoviz-topics/panel-chat-examples/blob/main/docs/examples/basics/basic_chat.py
"""
import panel as pn
from openai import OpenAI
from gnews import GNews
from scipy.spatial import KDTree
import numpy as np

from rag_news import TOPICS, get_news_by_topic, EmbeddingsStore, get_descriptions


client = OpenAI()
google_news = GNews()

pn.extension()


store = EmbeddingsStore()


def topic_classifier(user_query):
    """Given a user query, return a topic that GNews can process"""
    topics_ = ", ".join(TOPICS)
    system_prompt = f"""
You're a system that determines the topic of a news question.

You must classify a user prompt into one of the following values:

{topics_}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What happened in soccer today?"},
            {"role": "system", "content": "SPORTS"},
            {"role": "user", "content": "I want to know biz news"},
            {"role": "system", "content": "BUSINESS"},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )
    topic = response.choices[0].message.content.upper()

    return "WORLD" if topic not in TOPICS else topic


def news_agent(user_query, verbose=False):
    """An agent that can retrieve news by topic and summarizes them"""
    # determine the topic based on the query
    topic = topic_classifier(user_query)

    if verbose:
        print(f"Topic: {topic}")

    # get news that correspond to the selected topic
    news = get_news_by_topic(topic)

    descriptions = get_descriptions(news)

    # compute the embeddings for the retrieved news
    embeddings = store.get_many(descriptions)

    # find the 10 most relevant news given the query
    kdtree = KDTree(np.array(embeddings))
    _, indexes = kdtree.query(store.get_one(user_query), k=3)

    descriptions_relevant = [descriptions[i] for i in indexes]

    descriptions_text = "\n\n##\n\n".join(descriptions_relevant)

    system_prompt = f"""
You are a helpful news assistant that can answer questions about today's news.

Here are the top news from today (separated by ##), use these to generate your answer,
and disregard news that are not relevant to answer the question:

{descriptions_text}
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
    return news_agent(contents)


chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "Ask me anything about today's news! You can deploy your own by signing up at https://ploomber.io",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="News summarizer",
    main=[chat_interface],
).servable()
