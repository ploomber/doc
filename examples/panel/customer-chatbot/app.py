"""
Customer chatbot.

Input:
Users can submit queries that describe the type of books they are looking for, e.g., suggest fiction novels.
Users can also ask the chat assistant for books by specific author, e.g., recommend books by Dan Brown.
Answers to user's queries will be based on the Goodreads dataset:
https://www.kaggle.com/datasets/cristaliss/ultimate-book-collection-top-100-books-up-to-2023

Application logic:
The app determines the closest matches by comparing user query's embedding to the available
book embeddings. Embeddings of books are pre-computed on the description column of every book
and stored in the assets/ folder.

Response:
The chat assistant then determines the top relevant answers shortlisted by comparing embeddings and
provides the top 5 recommendations.
"""

import json

import panel as pn
from openai import OpenAI
from scipy.spatial import KDTree
import numpy as np
import pandas as pd
from pathlib import Path
from _wandb import WeightsBiasesTracking
import datetime

from util import get_embedding_from_text

ORDER_CANCEL = False

WEIGHTS_AND_BIASES_TRACKING = False

if WEIGHTS_AND_BIASES_TRACKING:
    wandb_client = WeightsBiasesTracking()


client = OpenAI()

df = pd.read_csv("orders.csv")


def detect_order_number(user_query):
    system_prompt = f"""
    You're a system that determines the invoice number or the order number in the user query. 

    You need to return only the order number.If no invoice number or order number is found 
    return the string None.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What were the items in order 536365?"},
            {"role": "system", "content": "536365"},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )
    invoice_number = response.choices[0].message.content
    print(f"invoice_number: {invoice_number}")
    return invoice_number if invoice_number != "None" else ""


def detect_intent(user_query):
    system_prompt = f"""
    You're a system that determines the intent of the user query. 

    You need to return only the intent and no additional sentences.
    If relevant intent is not found then return the string None.

    Valid intents = ["TOTAL_ORDER_COST", "CANCEL", "NUMBER_OF_ITEMS", "ORDER_ITEM_DETAILS", "CUSTOMER_ORDERS"]
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What is the total cost of the order 536365"},
            {"role": "system", "content": "TOTAL_ORDER_COST"},
            {"role": "user", "content": "total cost of all items in the order 536365"},
            {"role": "system", "content": "TOTAL_ORDER_COST"},
            {"role": "user", "content": "Which items were ordered in 536364"},
            {"role": "system", "content": "ORDER_ITEM_DETAILS"},
            {"role": "user", "content": "Can i cancel the order 458891"},
            {"role": "system", "content": "CANCEL"},
            {"role": "user", "content": "How many items were ordered in Invoice 558420"},
            {"role": "system", "content": "NUMBER_OF_ITEMS"},
            {"role": "user", "content": "Purchases made by Customer ID 17850"},
            {"role": "system", "content": "CUSTOMER_ORDERS"},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )
    intent = response.choices[0].message.content
    return intent if intent != None else ""


def cancel_order(invoice_number):
    cancel = {}
    print(df.head())
    invoice_details = df.loc[df['InvoiceNo'] == invoice_number]
    print(len(invoice_details))
    if len(invoice_details) == 0:
        cancel['eligible'] = False
        cancel['reason'] = f"Order not found: {invoice_number}"
        ORDER_CANCEL = False
        return cancel

    invoice_date = invoice_details.iloc[0]['InvoiceDate']
    print(f"invoice_date: {invoice_date}")
    date_object = datetime.datetime.strptime(invoice_date.split()[0], "%d/%m/%y")
    print(date_object)
    start_date = datetime.datetime(2010, 11, 1)
    end_date = datetime.datetime(2010, 12, 2)
    if start_date < date_object < end_date:
        cancel['eligible'] = True
        ORDER_CANCEL = True
        return cancel
    else:
        cancel['eligible'] = False
        cancel['reason'] = f"Order {invoice_number} not eligible for cancellation."
        ORDER_CANCEL = False
        return cancel


def customer_chatbot_agent(user_query, verbose=False, tracking=False):
    """An agent that can respond to customer's queries regarding orders"""

    if ORDER_CANCEL and "yes" in user_query:
        ORDER_CANCEL = False
        return f"Order successfully cancelled"

    invoice_number = detect_order_number(user_query)
    if not invoice_number:
        return "Please provide an Order ID"
    intent = detect_intent(user_query)
    print(intent)
    if not intent:
        return "Please provide more details regarding the action you want to take on the order."

    if intent != "CANCEL":
        return "We only support order cancellation requests. "

    return cancel_order(invoice_number)

    return "Sorry, we couldn't understand your query!"

    # start_time_ms = datetime.datetime.now().timestamp() * 1000
    #
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_query},
    #     ],
    #     seed=42,
    #     n=1,
    # )
    #
    # end_time_ms = round(datetime.datetime.now().timestamp() * 1000)
    #
    # if tracking:
    #     wandb_client.create_trace(system_prompt, response, user_query, start_time_ms, end_time_ms)

    # return response.choices[0].message.content


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    return customer_chatbot_agent(contents, tracking=WEIGHTS_AND_BIASES_TRACKING)


chat_interface = pn.chat.ChatInterface(callback=callback, callback_exception='verbose')
chat_interface.send(
    "I am a customer chat assistant! "
    "Currently we support only order cancellations. Please mention Order ID in your request."
    "You can deploy your own by signing up at https://ploomber.io",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="Customer Chatbot",
    main=[chat_interface],
).servable()
