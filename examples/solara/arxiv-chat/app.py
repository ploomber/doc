""" Arxiv Summarizer

We use Open AI and Arxiv to fetch, summarize, and provide additional info on scientific articles.

Inspired by: [Python: How to Build a ChatGPT Interface with Solara](https://itnext.io/python-how-to-build-a-chatgpt-interface-in-solara-fd6a1e15ef95)
Logos from: [FlatIcon](https://www.flaticon.com/)

## Note

Install pandas and tiktoken with `pip install pandas tiktoken`

"""

import solara as sl
from chat import Chat

css = """
    .main {
        width: 100%;
        height: 100%;
        max-width: 1200px;
        margin: auto;
        padding: 1em;
    }

    .logo {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: 2px solid transparent;
        overflow: hidden;
        display: flex;
    }

    .logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
"""

@sl.component
def Page() -> None:
    sl.Style(css)
    with sl.VBox(classes=["main"]):
        sl.HTML(tag="h1", style="margin: auto; padding-bottom: 10px;", unsafe_innerHTML="Arxiv Chat")
        Chat()
    with sl.Column(align="start"):
        with sl.HBox(align_items="center"):
            sl.Image(f"static/system-logo.png", classes=["logo"])
            sl.HTML(tag="a", unsafe_innerHTML="Built by Ploomber", attributes={"href": "https://ploomber.io", "target": "_blank"}, classes=["link"])

Page()