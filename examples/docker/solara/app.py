import requests
from typing import Optional, cast

import spacy
import pandas as pd
import pytextrank
import yake
import solara
import solara.lab
from solara.components.file_drop import FileDrop

solara.app_name = "Keyword Extraction App"


# Reference: https://climatechange.chicago.gov/climate-impacts/climate-impacts-agriculture-and-food-supply
response = requests.get("https://raw.githubusercontent.com/ploomber/doc/main/examples/docker/solara/sample.txt")

text_sample = response.text.lower()


class State:
    min_ngrams = solara.reactive(3)
    max_ngrams = solara.reactive(4)
    text = solara.reactive(cast(Optional[str], None))
    package = solara.reactive("PyTextRank")
    results = solara.reactive(50)
    stopwords = solara.reactive(False)

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
    package = State.package.value
    results = State.results.value
    stopwords = State.stopwords.value

    with solara.AppBarTitle():
        solara.Text("Keyword Extraction App")

    with solara.Card(title="About", elevation=6, style="background-color: #f5f5f5;"):
        solara.Markdown("""This Solara app is designed for performing keyword extraction from text documents.
                        Currently, it supports the packages `PyTextRank` and `Yake` for extracting the relevant keywords.
                        You may load the sample dataset or upload a custom one. The keywords list can be customized
                        by varying the `NGram` range (number of tokens in keyword) and whether or not to include stopwords.
                        The `Download Keywords` button can be used to download the keywords in `.csv` format""")

    with solara.Sidebar():
        with solara.Card("Controls", margin=0, elevation=0):
            with solara.Column():
                with solara.Row():
                    solara.Button("Sample dataset", color="primary", text=True, outlined=True, on_click=State.load_sample)
                    solara.Button("Clear dataset", color="primary", text=True, outlined=True, on_click=State.reset)
                FileDrop(on_file=State.load_from_file, on_total_progress=lambda *args: None, label="Drag a .txt file here")
                if text is not None:
                    solara.Select(label="Package", value=State.package, values=['PyTextRank', 'Yake'])
                    solara.InputInt("Number of results", value=State.results, continuous_update=True)
                    solara.SliderInt(label="Minimum Ngram", value=State.min_ngrams, min=1, max=10)
                    solara.SliderInt(label="Maximum Ngram", value=State.max_ngrams, min=1, max=10)
                    solara.Checkbox(label="Remove stopwords", value=State.stopwords)
                solara.Markdown("Hosted in [Ploomber Cloud](https://ploomber.io/)")

    if text is not None:
        nlp = spacy.load("en_core_web_sm")
        if stopwords:
            doc = nlp(text)
            text = ' '.join([token.text for token in doc if not token.is_stop])

        if package == "PyTextRank":
            # add PyTextRank to the spaCy pipeline
            nlp.add_pipe("textrank")
            doc = nlp(text)
            phrases_data = []
            for phrase in doc._.phrases:
                phrase_ngrams = len(phrase.text.split())
                if State.min_ngrams.value <= phrase_ngrams <= State.max_ngrams.value:
                    phrases_data.append([phrase.text, phrase.rank])
            if phrases_data:
                phrases_data = phrases_data[:results]
                # Create a DataFrame
                keywords_df = pd.DataFrame(phrases_data, columns=['Text', 'Rank']).sort_values(by='Rank', ascending=False)
                solara.DataFrame(keywords_df)
                solara.FileDownload(keywords_df.to_csv(index=False), label=f"Download keywords",
                                    filename="keyowrds.csv")
            else:
                solara.Info("No keywords found")
        elif package == "Yake":
            kw_extractor = yake.KeywordExtractor()
            keywords = kw_extractor.extract_keywords(text)
            valid_keywords = [keyword for keyword in keywords if
                              State.min_ngrams.value <= len(keyword[0].split()) <= State.max_ngrams.value]
            if valid_keywords:
                valid_keywords = valid_keywords[:results]
                keywords_df = pd.DataFrame(valid_keywords, columns=["Keyword", "Rank"]).sort_values(by='Rank', ascending=False)
                solara.DataFrame(keywords_df)
                solara.FileDownload(keywords_df.to_csv(index=False), label=f"Download keywords",
                                    filename="keyowrds.csv")
            else:
                solara.Info("No keywords found")

    else:
        solara.Info("No data loaded, click on the sample dataset button to load a sample dataset, or upload a file.")


@solara.component
def Layout(children):
    route, routes = solara.use_route()
    return solara.AppLayout(children=children)
