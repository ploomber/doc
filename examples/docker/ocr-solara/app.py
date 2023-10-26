import requests
import solara
import solara.lab
from solara.components.file_drop import FileDrop, FileInfo
from solara.alias import rv
import easyocr
from pathlib import Path


reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)


class State:
    image = solara.reactive(None)
    new_image_loaded = solara.reactive(False)
    extraction_complete = solara.reactive(False)
    extracted_text = solara.reactive("")

    @staticmethod
    def load_sample():
        image_path = Path("label.png")
        State.image.value = image_path.read_bytes()
        State.new_image_loaded.value = True
        State.extracted_text.value = reader.readtext(State.image.value, detail=0)
        State.extraction_complete.value = True
        
    @staticmethod
    def load_from_file(file):
        State.extraction_complete.value = False
        State.image.value = file["file_obj"].read()
        State.new_image_loaded.value = True
        State.extracted_text.value = reader.readtext(State.image.value, detail=0)
        State.extraction_complete.value = True

    @staticmethod
    def reset():
        State.image.value = None
        State.new_image_loaded.value = False
        State.extraction_complete.value = False
        State.extracted_text.value = ""

@solara.component
def Page():

    image = State.image.value

    with solara.AppBarTitle():
        solara.Text("OCR App")

    with solara.Card(title="About", elevation=6, style="background-color: #f5f5f5;"):
        solara.Markdown("""This Solara app is designed for extracting text from images""")

    with solara.Sidebar():
        with solara.Card("Controls", margin=0, elevation=0):
            with solara.Column():
                with solara.Row():
                    solara.Button("Sample image", color="primary", text=True, outlined=True, on_click=State.load_sample)
                    # solara.Button("Clear image", color="primary", text=True, outlined=True, on_click=State.reset)
                FileDrop(on_file=State.load_from_file, label="Drag an image file here")

                solara.Markdown("Hosted in [Ploomber Cloud](https://ploomber.io/)")

    if State.new_image_loaded.value and State.extraction_complete.value == False:
        with solara.Div():
            solara.Text("Extracting text...")
            solara.ProgressLinear(True)

    if State.extraction_complete.value:
        with solara.HBox():
            with solara.Card():
                solara.Image(image, format="jpeg")
            with solara.Card():
                if State.extracted_text.value:
                    solara.HTML(tag="h3", style="margin: auto;", unsafe_innerHTML="Extracted text")
                    solara.Markdown('\n'.join(State.extracted_text.value))
                else:
                    solara.Markdown("No text found")

    if State.image.value is None:
        solara.Info("No image loaded, click on the sample image button to load a sample image, or upload a file.")

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)
