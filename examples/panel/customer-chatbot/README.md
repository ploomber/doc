# Customer Chatbot

A chat assistant that helps customers perform actions on their orders.

The following actions are supported:

1. Get all orders placed by given customer
2. Get order details of a specific order
3. Allow cancellation of a particular order if has been placed in the last 14 days

![](screenshot.webp)

## Set key

To run this example you need to set the `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=<your_api_key> 
```

## Dataset

Download the [dataset](https://archive.ics.uci.edu/dataset/352/online+retail) to the `customer-chatbot/` folder, and rename it as `orders.csv`. 

## Deployment

Create a zip of `app.py`, `orders.csv` and `requirements.txt` and follow the instructions for deploying a [Panel](https://docs.cloud.ploomber.io/en/latest/apps/panel.html) application.
You also need to set `OPENAI_API_KEY` as an [environment variable](https://docs.cloud.ploomber.io/en/latest/user-guide/secrets.html) while deploying the application.