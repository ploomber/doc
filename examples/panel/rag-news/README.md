# News summarizer

To download today's news and compute the embeddings you first need to set the OpenAI key:

```bash
OPENAI_API_KEY=<your_api_key> 
```

Then run the below command to download the news:

```sh
python rag_news.py
```

Running the above command will generate a `embeddings.json` file and a `news` folder. Create a zip 
from all the files and follow the instructions for deploying a [Panel](https://docs.cloud.ploomber.io/en/latest/apps/panel.html) application.
You also need to set `OPENAI_API_KEY` as an [environment variable](https://docs.cloud.ploomber.io/en/latest/user-guide/env-vars.html) while deploying the application.