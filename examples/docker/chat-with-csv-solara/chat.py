import io
import tempfile
from pathlib import Path
from dataclasses import dataclass

import pandas as pd
import solara as sl
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

plt.switch_backend("agg")


chatbox_css = """
.message {
    max-width: 450px;
    width: 100%;
}

.user-message, .user-message > * {
    background-color: #f0f0f0 !important;
}

.assistant-message, .assistant-message > * {
    background-color: #9ab2e9 !important;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid transparent;
  overflow: hidden;
  display: flex;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
"""


@dataclass
class Message:
    role: str
    content: str
    df: pd.DataFrame
    fig: Figure


def ChatBox(message: Message) -> None:
    sl.Style(chatbox_css)

    align = "start" if message.role == "assistant" else "end"
    with sl.Column(align=align):
        with sl.Card(classes=["message", f"{message.role}-message"]):
            if message.content:
                sl.Markdown(message.content)
            elif message.df is not None:
                with sl.Card():
                    sl.DataFrame(message.df)
                with sl.Card():
                    sl.FileDownload(message.df.to_csv(index=False), filename="data.csv", label="Download file")
            elif message.fig is not None:
                with sl.Card():
                    sl.FigureMatplotlib(message.fig)
                with sl.Card():
                    buf = io.BytesIO()
                    message.fig.savefig(buf, format="jpg")
                    fp = tempfile.NamedTemporaryFile()
                    with open(f"{fp.name}.jpg", 'wb') as ff:
                        ff.write(buf.getvalue())
                    buf.close()
                    file_object = sl.use_memo(lambda: open(f"{fp.name}.jpg", "rb"), [])
                    sl.FileDownload(file_object, mime_type="image/jpeg", close_file=False)

        # Image reference: https://www.flaticon.com/free-icons/bot;
        #                  https://www.flaticon.com/free-icons/use

        with sl.HBox(align_items="center"):
            image_path = Path(f"static/{message.role}-logo.png")
            sl.Image(str(image_path), classes=["avatar"])
            sl.Text(message.role.capitalize())
