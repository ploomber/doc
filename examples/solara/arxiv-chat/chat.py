import solara as sl
from solara.alias import rv
from dataclasses import dataclass
import ai
import articles as art
from scipy.spatial import KDTree
import numpy as np

chatbox_css = """
a: {
    text-decoration: none;
    color: black;
}

.message {
    max-width: 450px;
    width: 100%;
}

.system-message, .system-message > * {
    background-color: #ffffff !important;
}

.user-message, .user-message > * {
    background-color: #f0f0f0 !important;
}

.assistant-message, .assistant-message > * {
    background-color: #9ab2e9 !important;
}



"""

@dataclass
class Message:
    role: str
    content: str


ac = art.ArxivClient()
oc = ai.OpenAIClient()
store = ai.EmbeddingsStore()

@sl.component
def Chat() -> None:
    sl.Style("""
        .chat-input {
            max-width: 800px;
        }

        .avatar {
            display: block;
            margin: auto;
            width: 50%;
        }
            
    """)

    messages, set_messages = sl.use_state([
        Message(
            role="assistant",
            content="Hi! Start by entering a math or science topic to learn about.")
        ]
    )

    loaded, set_loaded = sl.use_state(False)
    disabled, set_disabled = sl.use_state(False)

    def load_articles_from_topic_query(query):
        _messages = messages + [Message(role="user", content=query)]
        set_messages(_messages + [Message(role="assistant", content="Processing...")])
        topic = oc.topic_classifier(query)

        if topic not in oc.categories:
            help_msg = "I'm having trouble understanding that. Can you please try again? \n\n I can help you with a wide range of topics, including but not limited to: mathematics, computer science, astrophysics, statistics, and quantitative biology!"
            set_messages(_messages + [Message(role="assistant", content=help_msg)])
            return

        articles_raw = ac.get_articles(topic)
        articles = ac.results_to_array(articles_raw)

        embeddings = store.get_many(articles)
        kdtree = KDTree(np.array(embeddings))
        _, indexes = kdtree.query(store.get_one(query), k=5)
        relevant_articles = [articles_raw[i] for i in indexes]

        ac.results_to_json(relevant_articles)
        print("CALLED LOAD FROM PAGE")
        oc.load_prompt()
        print("CALLED CHAT FROM PAGE")
        for new_message in oc.article_chat("Summarize each article in a sentence"):
            set_messages(_messages + [Message(role="assistant", content=f"Fetched some articles. Here's a summary: \n\n{new_message}")])

        set_loaded(True)


    def ask_chatgpt(input):
        set_disabled(True)
        _messages = messages + [Message(role="user", content=input)]
        set_messages(_messages)
        if not loaded:
            print("Called load articles from ask_chatgpt")
            load_articles_from_topic_query(input)
        else:
            print("Called chat from ask_chatgpt")
            for new_message in oc.article_chat(input):
                set_messages(_messages + [Message(role="assistant", content=new_message)])

        set_disabled(False)

    with sl.lab.ChatBox(style={"height": "70vh"}):
        for message in messages:
            with sl.lab.ChatMessage(
                user=message.role=="user",
                avatar=sl.Image(f"static/{message.role}-logo.png", classes=["avatar"]),
                avatar_background_color="#ffffff",
                name=message.role.capitalize(),
                color="#7baded" if message.role == "user" else "rgba(0,0,0, 0.06)",
                notch=True,
            ):
                sl.Markdown(message.content)

    sl.lab.ChatInput(send_callback=ask_chatgpt, disabled=disabled)

