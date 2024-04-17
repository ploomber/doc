# GPUs

```{note}
We're giving way free GPUs for a week to test our system. Email us at
[contact@ploomber.io](mailto:contact@ploomber.io) if you want access.
```

To deploy a GPU, first, [create an account](https://platform.ploomber.io/register?utm_source=gpu&utm_medium=documentation). Then, select the `Docker` option:

![](../static/docker.png)

In the `Source code` section, drop a `.zip` file with your code. Or use one of the examples (download them and zip them):

::::{grid} 2 2 3 3
:class-container: text-center
:gutter: 2

:::{grid-item-card} 🌔 Image Q&A
:link: https://github.com/ploomber/doc/tree/main/examples/fastapi/describe-image-backend
FastAPI app that uses moondream2 to answer questions about an uploaded image.
:::

:::{grid-item-card} 🦙 llama-cpp server
:link: https://github.com/ploomber/doc/tree/main/examples/docker/llama-cpp-server
A a web server that allows using Llama 2
:::

:::{grid-item-card} 🪐 JupyterLab
:link: jupyter-remote-gpu
:link-type: ref
Connect to a remote Jupyter server to fine-tune LLMs.
:::

::::


Then, in the deployment form, select `1 GPU` in the `Advanced` section:

![](../static/gpu/select-gpu.png)

Currently, only `1 GPU` is supported, which will deploy your application on a
machine with an NVIDIA T4 (16GB), 4 CPUs and 16 GB of RAM.
