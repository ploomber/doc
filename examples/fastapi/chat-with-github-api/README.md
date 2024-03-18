# Chat with Github repo API - Instructions incomplete

## Running the app

First, install the requirements

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

Now, in another terminal, make sure you set these environment variables:

```
OPENAI_API_KEY=your-key
GITHUB_TOKEN=your-github-pat
```

Then start Celery:

```
watchmedo auto-restart --directory=./ --pattern=task.py -- celery --app=task.app worker --concurrency=1 --loglevel=DEBUG
```

This will watch for any changes you make and automatically reload.

## Testing the app

I've designed a small CLI tool to test the API. It accepts the commands `index`, `scrape`, `status`, `ask`, and `clear`.

Test the API is working:

`python test.py index`

These call the respective API endpoints. For example, 

To scrape a repo, run `python test.py scrape <owner> <repo-name> <branch-name>`:

e.g. `python test.py scrape ploomber doc main`

To check the status of a repo:

`python test.py status <repo-id>`

Ask a question:

`python test.py ask <repo-id> <question>`

To clear the database:

`python test.py clear`