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
            content="""Hi! I'm an assistant to help you find academic papers using Arxiv!  \
                Start by entering a math, science, or technology topic to learn about.  \
                Once I find you a set of articles, I can provide detailed information on each article including:  \
                author, description, category, published date, and download link."""
        )
    ])

    loaded, set_loaded = sl.use_state(False)
    disabled, set_disabled = sl.use_state(False)

    def load_articles_from_topic_query(query):
        _messages = messages + [Message(role="user", content=query)]
        set_messages(_messages + [Message(role="assistant", content="Processing...")])
        criterion, order = oc.call_fetch_articles_tool_for_query_params(query)
        success, content = oc.fetch_articles_from_query(query, criterion, order)

        if not success:
            set_messages(_messages + [Message(role="assistant", content=content)])
            return

        for new_message in oc.article_chat("Summarize each article in a sentence. Number them, and format like title: summary. Do not call a function."):
            set_messages(_messages + [Message(role="assistant", content=f"Fetched some articles.\n\n{new_message}")])

        set_loaded(True)


    def ask_chatgpt(input):
        set_disabled(True)
        _messages = messages + [Message(role="user", content=input)]
        set_messages(_messages)
        if not loaded:
            load_articles_from_topic_query(input)
            set_disabled(False)
            return
        
        for new_message in oc.article_chat(input):
            if new_message == "":
                set_messages(_messages + [Message(role="assistant", content="Processing...")])
        
            elif new_message == "FETCHED-NEED-SUMMARIZE":
                for msg in oc.article_chat("Summarize each article in a sentence. Number them, and format like title: summary."):
                    set_messages(_messages + [Message(role="assistant", content=msg)])
        
            else:
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
                if message.content.startswith("http"):
                    sl.HTML(tag="a", unsafe_innerHTML=message.content, attributes={"href": message.content, "target": "_blank"})
                else:
                    sl.Markdown(message.content)

    sl.lab.ChatInput(send_callback=ask_chatgpt, disabled=disabled)

