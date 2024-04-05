# Private ChatGPT

A basic Chainlit chat UI to be used with an LLM hosted and served via vLLM.

## Deployment instructions:

Ensure your LLM has already been deployed.

If you configured a private API key on the backend, set it here via a secret or `.env` file:

```sh
export VLLM_API_KEY=your_key
```

Note down the host URL. In `app.py`, modify `api_base` with your host URL.

Then, initialize and deploy:

```sh
ploomber-cloud init
ploomber-cloud deploy --watch
```