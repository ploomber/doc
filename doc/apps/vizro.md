---
myst:
  html_meta:
    description: Deploy a Vizro app on Ploomber in seconds with this guide.
    keywords: vizro, deployment, hosting
    property=og:title: Vizro | Ploomber Docs
    property=og:description: Deploy Vizro app on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-vizro.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/vizro.html
---

# Vizro

To deploy a [Vizro](https://vizro.readthedocs.io/en/stable/) application you need a [Ploomber Cloud](https://platform.ploomber.io/register?utm_source=dash&utm_medium=documentation) account. 

## Project Structure

Your deployment package must include these three essential files:

1. `app.py` - Main application file
2. `requirements.txt` - Python dependencies
3. `Dockerfile` - Container configuration

You can get started quickly using our template repository.

## Application Setup

1. Main Application File (`app.py`)

Your `app.py` should initialize the Vizro application as follows:

```python
import vizro as vm
from vizro import Vizro

# Initialize your dashboard
dashboard = vm.Dashboard(pages=[page])

# Create the application instance
app = Vizro().build(dashboard)

# Development server (optional)
if __name__ == "__main__":
    app.run()
```

2. Dependencies File (`requirements.txt`)

List all Python packages required by your application.

3. `Dockerfile`

Create a `Dockerfile` with this configuration:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn vizro

# Copy application files
COPY . .

# Configure the container
EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "4", "--threads", "2", "app:app"]
```

## Testing locally

Before deployment, test your application locally using Docker:

```sh
# build the docker image
docker build . -t vizro-app

# run it
docker run -p 5000:80 vizro-app
Now, open http://0.0.0.0:5000/ to see your app.
```

Once running, access your application at http://localhost:5000

## Deploy

Deployment Process

1. Zip all project files (`app.py`, `requirements.txt`, `Dockerfile`, and any additional resources)
2. Log in to Ploomber Cloud
3. Navigate to the deployment menu
4. Select the Docker deployment option
5. Upload your zip file

![](../static/docker.png)

```{tip}
To ensure your app doesn't break on re-deployments, pin your [dependencies.](pin-dependencies)
```
