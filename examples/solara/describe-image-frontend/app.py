from os import environ

import requests
import solara
from solara.components.file_drop import FileInfo

BASE_URL = environ["API_BASE_URL"]


def describe_image(image_bytes, question):
    url = f"{BASE_URL}/describe"
    params = {"question": question}

    files = {"file": image_bytes}
    response = requests.post(url, files=files, params=params)
    return response.json()["description"]


@solara.component
def Page():
    default_question = "What is in this image?"

    content, set_content = solara.use_state(b"")
    is_loading, set_loading = solara.use_state(False)

    output, set_output = solara.use_state("")
    question, set_question = solara.use_state(default_question)

    def on_file(file: FileInfo):
        f = file["file_obj"]
        set_content(f.read())
        set_output("")

    def on_click():
        if not content or not question:
            return

        set_loading(True)
        model_output = describe_image(content, question)
        set_loading(False)
        set_output(model_output)

    def on_click_random_image():
        url = "https://source.unsplash.com/random"
        response = requests.get(url)
        set_content(response.content)
        set_output("")

    def on_value(value):
        set_question(value)

    with solara.Column():
        solara.Title("Chat with an image (powered by moondream2 and Ploomber Cloud)")

        with solara.Sidebar():
            solara.Button(label="Load random image", on_click=on_click_random_image)

            solara.FileDrop(
                label="Drop an image here...",
                on_file=on_file,
                lazy=True,
            )

            solara.InputText(
                "Type your question here...",
                on_value=on_value,
                value=default_question,
            )

            solara.Button(label="Submit", color="primary", on_click=on_click)

        if not content:
            solara.Warning("Please drop an image first!")
        elif not question:
            solara.Warning("Please type a question first!")

        if content:
            with solara.Card():
                solara.Image(content, width="50%")

        if is_loading and content:
            solara.SpinnerSolara(size="100px")
        elif output:
            with solara.Card():
                solara.Text(output)
