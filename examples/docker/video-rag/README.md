## RAG from video

This is a full stack project that uses a video as input, populates an ElasticSearch instance with vectors through an indexing pipeline, and initializes a retriver pipeline with a Solara app.

A complete walk through of this application can be found [here](https://ploomber.io/blog/rag-video-app/)

### Requirements

- Python 3.11
- Docker
- OpenAI Key

### Installation

1. Clone the repository
2. Create a virtual environment with with Python 3.11 and activate it
3. Install the requirements through the `requirements.txt` file

### If you are running a local ElasticSearch instance

Use docker-compose to run the ElasticSearch instance

```bash
docker-compose up -d
```

### If you are running a remote ElasticSearch instance

Create a `.env` file with the following variables:

```bash
elastic_search_host=<host>
elastic_username=<username>
elastic_password=<password>
OPENAI=<key>
```

Replace host, username, and password with the corresponding values for your cloud-based instance.

Modify the document store in `video_indexing.py` and `app.py` to use the remote instance.

### Execution of indexing pipeline

```bash
python indexing_pipeline.py
```

### Execution of retriever pipeline through the Solara app

```bash
cd app/
solara run app.py
```