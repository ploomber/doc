# GPUs

```{note}
We're giving way free CPUs for a week to test our system. Email us at
[contact@ploomber.io](mailto:contact@ploomber.io) if you want access.
```

To deploy an application that requires a GPU, select `1 GPU` in the `Advanced` section
when deploying your application:

![](../static/gpu/select-gpu.png)

Currently, only `1 GPU` is supported, which will deploy your application on a
machine with an NVIDIA T4 (16GB), 4 CPUs and 16 GB of RAM.

You need to deploy via the `Docker` option for your app to be able to use the GPU:

![](../static/docker.png)

Here are some examples:

- [FastAPI app](https://github.com/ploomber/doc/tree/main/examples/fastapi/describe-image-backend) that uses moondream2 so you can ask questions about an uploaded image
- [llama-cpp server](https://github.com/ploomber/doc/tree/main/examples/docker/llama-cpp-server) a web server that allows using Llama 2