# Chat with Github repo API - Instructions incomplete

## Running the app

First, make sure you set these environment variables:

```
OPENAI_API_KEY=your-key
GITHUB_TOKEN=your-github-pat
```

Then, install the requirements

```
pip install -r requirements.txt
```

### Start the API server

Set up the database:

```
python models.py
```

To start the API, run

```
uvicorn app:app --reload
```

### Celery

Make sure you have Docker running.

In another terminal, start Redis:

```
docker run --rm --name some-redis -p 6379:6379 redis:latest
```

Now, in another terminal, start Celery:

```
watchmedo auto-restart --directory=./fastapi_celery --pattern=task.py -- celery --app=fastapi_celery.task.app worker --concurrency=1 --loglevel=DEBUG
```

This will watch for any changes you make and automatically reload.

## Testing the app

I've designed a small CLI tool to test the api. It accepts the commands `index`, `scrape`, `status`, `ask`, and `clear`.

These call the respective API endpoints. For example, to scrape a repo, run `python test.py scrape owner repo-name branch-name`:

`python test.py ploomber doc main`
