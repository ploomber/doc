from typing import Optional, cast

import pandas as pd
import requests

import solara
import solara.express as solara_px  # similar to plotly express, but comes with cross filters
import solara.lab
from solara.components.columns import Columns
from solara.components.file_drop import FileDrop

import spacy
import pytextrank


try:
    # fails on pyodide
    # Reference: https://climatechange.chicago.gov/climate-impacts/climate-impacts-agriculture-and-food-supply
    response = requests.get("https://raw.githubusercontent.com/ploomber/doc/958c2cfc9ca2892f3b529ee002fdecd2418af36c/examples/docker/solara/sample.txt")
    text_sample = response.text.lower()
except:  # noqa
    text_sample = None


class State:
    min_ngrams = solara.reactive(3)
    max_ngrams = solara.reactive(4)
    text = solara.reactive("")

    @staticmethod
    def load_sample():
        State.text.value = text_sample
        
    @staticmethod
    def load_from_file(file):
        State.text.value = file["file_obj"].read().decode("utf-8")

    @staticmethod
    def reset():
        State.text.value = None


@solara.component
def Page():
    text = State.text.value

    with solara.Sidebar():
        with solara.Card("Controls", margin=0, elevation=0):
            with solara.Column():
                with solara.Row():
                    solara.Button("Sample dataset", color="primary", text=True, outlined=True, on_click=State.load_sample)
                    solara.Button("Clear dataset", color="primary", text=True, outlined=True, on_click=State.reset)
                FileDrop(on_file=State.load_from_file, on_total_progress=lambda *args: None, label="Drag a .txt file here")

                

                if text is not None:
                    solara.SliderInt(label="Minimum Ngram", value=State.min_ngrams, min=1, max=10)
                    solara.SliderInt(label="Maximum Ngram", value=State.max_ngrams, min=1, max=10)


    if text is not None:
        nlp = spacy.load("en_core_web_sm")
        
        # add PyTextRank to the spaCy pipeline
        nlp.add_pipe("textrank")
        doc = nlp(text)
        phrases_data = []
        for phrase in doc._.phrases:
            phrase_ngrams = len(phrase.text.split())
            if phrase_ngrams >= State.min_ngrams.value and phrase_ngrams <= State.max_ngrams.value:
                phrases_data.append([phrase.text, phrase.rank, phrase.count])
        if phrases_data:
        # Create a DataFrame
            keywords_df = pd.DataFrame(phrases_data, columns=['Text', 'Rank', 'Count']).sort_values(by='Rank', ascending=False)
            solara.DataFrame(keywords_df)

            solara.FileDownload(keywords_df.to_csv(index=False), label=f"Download keywords", filename="keyowrds.csv")

        else:
            solara.Info("No keywords found. Try changing the NGrams minimum and maximum value")


    else:
        solara.Info("No data loaded, click on the sample dataset button to load a sample dataset, or upload a file.")

    



@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)
