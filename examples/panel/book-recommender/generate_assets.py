import json
import argparse
import pandas as pd
from pathlib import Path
from openai import OpenAI

from util import get_embedding_from_text

# Download the dataset from:
# https://www.kaggle.com/datasets/cristaliss/ultimate-book-collection-top-100-books-up-to-2023
df = pd.read_csv(Path("goodreads.csv"))

client = OpenAI()


def generate_embeddings(rows, verbose=False):
    """Function to generate an embeddings.json file that contains
    mapping {title: embedding} where embeddings are generated on the
    description column of goodreads.csv file.
    """

    final_df = df.head(rows) if rows else df
    embeddings_json = {}
    if verbose and rows:
        print(f"Generating embeddings for {rows} rows")
    for index, row in final_df.iterrows():
        if verbose:
            print(f"Row number: {index}")
        embeddings_json[row["title"]] = get_embedding_from_text(row["description"])
    path = Path("assets", "embeddings.json")
    with open(path, 'w') as f:
        json.dump(embeddings_json, f)
    if verbose:
        print(f"Generated embeddings of description column at '{path}'")


def generate_lookup(verbose=False):
    """Function to generate mappings between columns for faster lookup"""
    author_to_title = df.groupby(df['authors'].str.upper())['title'].apply(list).to_dict()
    path = Path("assets", "author_to_title.json")
    with open(path, 'w') as f:
        json.dump(author_to_title, f)
    if verbose:
        print(f"Generated author to title mappings at '{path}'")
    title_to_description = df.groupby(df['title'].str.upper())['description'].apply(list).to_dict()
    path = Path("assets", "title_to_description.json")
    with open(path, 'w') as f:
        json.dump(title_to_description, f)
    if verbose:
        print(f"Generated title to description mappings at '{path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true', help='Debug')
    parser.add_argument('--embeddings', action='store_true', help='Generate embeddings')
    parser.add_argument("-n", "--rows", required=False, help="Number of rows to limit for generating embeddings")
    args = parser.parse_args()
    assets_path = Path("assets")
    if not assets_path.exists():
        Path("assets").mkdir()
    generate_lookup(args.verbose)
    rows = int(args.rows) if args.rows else None
    if args.embeddings:
        generate_embeddings(rows, args.verbose)

