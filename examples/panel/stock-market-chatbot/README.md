## LLM-powered Stock Market app with Panel

This application downloads stock market data from Yahoo Finance, populates a duckdb instance, generates a time series plot of the selected stocks. It also allows the user to ask a natural language question about the plot and get a response using the LLM model.

The app is built using Python Yahoo Finance [yfinance](https://pypi.org/project/yfinance/), [Panel](https://panel.holoviz.org/),[DuckDB](https://duckdb.org/), OpenAI's [Vision Model preview API](https://platform.openai.com/docs/guides/vision) and [ImageKit](https://docs.imagekit.io/getting-started/quickstart-guides/python/python_app). The app can be hosted on [Ploomber Cloud](https://www.platform.ploomber.io/).

The app will store the plot generated and save it to ImageKit.io, and then use the OpenAI API to generate a response to the user's question about the plot. 

### Pre-requisites

1. OpenAI API key. Visit their [Documentation](https://platform.openai.com/docs/api-reference/introduction)
2. ImageKit.io url endpoint, public key, and private key. Visit their [Dashboard](https://imagekit.io/dashboard)

To run the app, you need to install the following packages:

```bash
conda create -n stock-market-chatbot python=3.10
conda activate stock-market-chatbot
pip install -r requirements.txt
```

### Running the app

```bash
panel serve app.py --autoreload --show
```

### Deploying the app to Ploomber Cloud

To deploy the app to Ploomber Cloud, you need to have a Ploomber Cloud account. Visit their [website](https://www.platform.ploomber.io/) to create an account. Once you have an account, you can deploy the Panel app to Ploomber Cloud using the following guides:

[Deploy Panel apps through the UI](https://docs.cloud.ploomber.io/en/latest/apps/panel.html).
[Add your secret variables](https://docs.cloud.ploomber.io/en/latest/user-guide/env-vars.html)