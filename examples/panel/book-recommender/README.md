# Book Recommender

A chat assistant for recommending books to the user based on inputs.

## Set key

To run this example you need to set the `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=<your_api_key> 
```

## Dataset

Download the [dataset](https://www.kaggle.com/datasets/cristaliss/ultimate-book-collection-top-100-books-up-to-2023) to the `book-recommender/` folder, and rename it as `goodreads.csv`. 


## Generate lookup files

Generate lookup files by running the following script:

```bash
python generate_assets.py
```

Running this command should generate `author_to_title.json` and `title_to_description.json` files in the `assets/` folder.

The `assets/embeddings.json` file contains embeddings of the description column of the dataset.
If you want to re-generate the `embeddings.json` file you can run:

```bash
python generate_assets.py -n 100 --embeddings --verbose
```

Here `-n 100` will generate embeddings for first 100 rows. If `-n` option is not provided the script will generate embeddings of all rows.

## Deployment

Create a zip of `app.py`, `util.py`, `requirements.txt` and `assets/` folder, and follow the instructions for deploying a [Panel](https://docs.cloud.ploomber.io/en/latest/apps/panel.html) application.
You also need to set `OPENAI_API_KEY` as an [environment variable](https://docs.cloud.ploomber.io/en/latest/user-guide/env-vars.html) while deploying the application.
