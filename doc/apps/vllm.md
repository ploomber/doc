---
myst:
  html_meta:
    description: Deploy a vLLM server on Ploomber in seconds with this guide.
    keywords: vllm, deployment, hosting
    property=og:title: vLLM | Ploomber Docs
    property=og:description: Deploy a vLLM server on Ploomber in seconds with this guide.
    property=og:image: https://docs.cloud.ploomber.io/en/latest/_static/opengraph-images-vllm.png
    property=og:url: https://docs.cloud.ploomber.io/en/latest/apps/vllm.html
---

# vLLM

You can deploy a GPU-powered vLLM server on Ploomber Cloud with a few clicks.

First, ensure you create a [Ploomber Cloud](https://platform.ploomber.io/register?utm_source=vllm&utm_medium=documentation) account Then, download the files from the [vLLM example.](https://github.com/ploomber/doc/tree/main/examples/docker/vllm-gpu) and create a `.zip` file.

```{important}
Modify the last line in the `Dockerfile` to serve whatever model you want.
```

## Deploy

To deploy a vLLM from the deployment menu, follow the Docker instructions:

![docker deployment menu](../static/docker.png)

Then, ensure you set an API key to protect your server by adding a `VLLM_API_KEY` secret (in the `Secrets` section).

To generate a value, you can run this in the terminal:

```sh
python -c 'import secrets; print(secrets.token_urlsafe())'
```

```{important}
If your model requires you to accept a license, you also need to pass a valid
`HF_TOKEN` in the secrets section so vLLM can download the weights.
```

Finally, ensure you select a GPU.

![gpu selection menu](../static/gpu/select-gpu.png)

Deployment will take ~10 minutes since Ploomber has to build your Docker image, deploy the server and download the model.

The server will be ready to take requests when the `WEBSERVICE LOGS` show something like this:

```
2024-03-28T01:09:58.367000 - INFO: Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
```

## Testing

Once your server is running, you can test it with the following script:

```python
# NOTE: remember to run: pip install openai
from openai import OpenAI

# we haven't configured authentication, so we just pass a dummy value
openai_api_key = "PUT_YOUR_API_KEY_HERE"

# modify this value to match your host, remember to add /v1 at the end
openai_api_base = "https://autumn-snow-1380.ploomberapp.io/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
completion = client.completions.create(model="google/gemma-2b", # set the right model name
                                      prompt="JupySQL is",
                                      max_tokens=20)
print(completion.choices[0].text)
```

```{note}
The previous snippet is using the `openai` Python package since vLLM exposes a server
that mimics OpenAI's API; however, you don't have to use it. You can also use an http
library like `requests`.
```