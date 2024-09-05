
Running multiple Streamlit apps in a single server.

## Run locally

```sh
docker build -t multiple-streamlit .
docker run -p 8080:80 multiple-streamlit
```

Then, open: http://localhost:8080

## Deployment

```sh
ploomber-cloud init
ploomber-cloud deploy
```