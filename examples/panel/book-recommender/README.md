# Book Recommender

To run this example you need to set the `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=<your_api_key> 
```

Create a zip from all the files and follow the instructions for deploying a [Panel](https://docs.cloud.ploomber.io/en/latest/apps/panel.html) application.
You also need to set `OPENAI_API_KEY` as an [environment variable](https://docs.cloud.ploomber.io/en/latest/user-guide/env-vars.html) while deploying the application.

To re-generate embeddings run the below command:

```bash
python rag_book_recommender.py
```

Copy the `embeddings.json` file to the `assets/` folder.