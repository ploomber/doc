import solara as sl
from chat import Chat

css = """
    .main {
        width: 100%;
        height: 90%;
        margin: auto;
        padding: 1em;
    }

    .plug {
        left: 0px; 
        bottom: 0px; 
        position: absolute; 
        padding: 10px;
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
def Page():
    sl.Style(css)
    with sl.VBox(classes=["main"]) as ch:
        Chat()
    
    return ch
    # with sl.Column(align="start", classes=["plug"]):
    #     with sl.HBox(align_items="center"):
    #         sl.Image(f"static/system-logo.png", classes=["logo"])
    #         sl.HTML(tag="a", unsafe_innerHTML="Built by Ploomber", attributes={"href": "https://ploomber.io", "target": "_blank"}, classes=["link"])

Page()