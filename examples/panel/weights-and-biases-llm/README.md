# Connect your Panel app to Weights and Biases

This example demonstrates how to connect your Panel app to Weights and Biases. We will use the [Weights and Biases](https://www.wandb.com/) API to track several metrics when making prompts against a GPT model from OpenAI. The final application enables you to monitor token usage, prompt length, and the number of tokens generated during a user session of the application running while it is deployed. 

## Running this application locally

To run this example locally, you can clone the repository and install the requirements.

### Install the requirements

To run this example, you will need to install the required libraries. You can do this by running the following commands:

```bash
git clone https://github.com/ploomber/doc.git
cd examples/panel/weights-and-biases-llm
conda env create --name wandbllm python=3.10
conda activate wandbllm
pip install -r requirements.txt
```

### Run the application locally

To run this example locally, you can use the following command:

```bash
panel serve app.py --autoreload --show
```

## Pre-requisites

To run this example, you will need to install the following libraries:

```bash
pip install -r requirements.txt
```