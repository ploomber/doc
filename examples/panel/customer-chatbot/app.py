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
import pandas as pd
import datetime

ORDER_CANCEL = None

client = OpenAI()

df = pd.read_csv("orders.csv")


def is_ready_for_cancellation():
    return ORDER_CANCEL


def detect_order_number_and_intent(user_query):
    """Function to detect Order ID (Invoice number) and intent in the
    user query"""

    system_prompt = f"""
        You're a system that determines the invoice number (order number) and the intent in the user query. 

        You need to return only the order number. If no invoice number or order number is found 
        return the string None.
        
        You need to return only the intent and no additional sentences.
        If relevant intent is not found then return the string None.

        Valid intents = ["TOTAL_ORDER_COST", "CANCEL", "NUMBER_OF_ITEMS", "ORDER_ITEM_DETAILS"]
        
        You should return the response as a JSON.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What is the total cost of the order 536365"},
            {"role": "system", "content": "{\"OrderID\":\"536365\", \"Intent\":\"TOTAL_ORDER_COST\"}"},
            {"role": "user", "content": "total cost of all items in the order 536365"},
            {"role": "system", "content": "{\"OrderID\":\"536365\", \"Intent\":\"TOTAL_ORDER_COST\"}"},
            {"role": "user", "content": "Which items were ordered in 536364"},
            {"role": "system", "content": "{\"OrderID\":\"536364\", \"Intent\":\"ORDER_ITEM_DETAILS\"}"},
            {"role": "user", "content": "Can i cancel the order 458891"},
            {"role": "system", "content": "{\"OrderID\":\"458891\", \"Intent\":\"CANCEL\"}"},
            {"role": "user", "content": "How many items were ordered in Invoice 558420"},
            {"role": "system", "content": "{\"OrderID\":\"558420\", \"Intent\":\"NUMBER_OF_ITEMS\"}"},
            {"role": "user", "content": "Order ID 17850"},
            {"role": "system", "content": "{\"OrderID\":\"17850\", \"Intent\":\"None\"}"},
            {"role": "user", "content": "all products"},
            {"role": "system", "content": "{\"OrderID\":\"None\", \"Intent\":\"None\"}"},
            {"role": "user", "content": user_query}
        ],
        seed=42,
        n=1,
    )
    output = response.choices[0].message.content
    print(f"JSON Output: {output}")
    return json.loads(output)


def cancel_order(invoice_number):
    global ORDER_CANCEL
    cancel = {}
    print(df.head())
    invoice_details = df.loc[df['InvoiceNo'] == invoice_number]
    print(len(invoice_details))
    if len(invoice_details) == 0:
        #invoice_details = df.loc[df['InvoiceNo'] == 'C'+invoice_number]
        cancel['eligible'] = False
        cancel['reason'] = f"Sorry! We couldn't find order: {invoice_number}. Please try another Order ID"
        ORDER_CANCEL = None
        return cancel

    invoice_date = invoice_details.iloc[0]['InvoiceDate']
    print(f"invoice_date: {invoice_date}")
    date_object = datetime.datetime.strptime(invoice_date.split()[0], "%m/%d/%y")
    print(date_object)
    start_date = datetime.datetime(2010, 11, 1)
    end_date = datetime.datetime(2010, 12, 2)

    if start_date < date_object < end_date:
        print("eligible")
        cancel['eligible'] = True
        ORDER_CANCEL = invoice_number
        return cancel
    else:
        cancel['eligible'] = False
        cancel['reason'] = f"Order {invoice_number} not eligible for cancellation."
        ORDER_CANCEL = None
        return cancel


def customer_chatbot_agent(user_query, verbose=False, tracking=False):
    """An agent that can respond to customer's queries regarding orders"""

    output = detect_order_number_and_intent(user_query)

    global ORDER_CANCEL

    if ORDER_CANCEL:
        if "yes" in user_query.lower():
            msg = f"Order {ORDER_CANCEL} successfully cancelled. Is there anything else we can help you with?"
            ORDER_CANCEL = None
            return msg
        else:
            return "Order not cancelled. Is there anything else we can help you with?"

    invoice_number = output["OrderID"]
    intent = output["Intent"]

    if invoice_number == "None":
        return "Please provide an Order ID"

    if intent == "None":
        return "Please provide more details regarding the action you want to take on the order."

    if intent != "CANCEL":
        return "We only support order cancellation requests. Please help us with the Order ID you want to cancel"
    else:
        cancellation = cancel_order(invoice_number)
        if cancellation["eligible"]:
            return "Please confirm that you want to cancel the order (Yes/No)"
        else:
            return cancellation['reason']

    return "Sorry, we couldn't understand your query!"


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    return customer_chatbot_agent(contents)


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
