"""
Customer chatbot.

Input:
Users can submit queries by specifying a certain action that they want the chat assistant to perform
on a particular Order ID.
Answers to user's queries will be based on the Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

Response:
Currently the chat assistant can perform only order cancellations. Given an Order ID it determines
if the Order ID exists and is eligible for cancellation. If so, it helps the customer cancel the order.
"""

import json
import math
import panel as pn
from openai import OpenAI
import pandas as pd
import datetime

CONTEXT_DATA = {
    "CancelOrderId": None,
    "CancelConfirmationPending": False,
    "CancelledOrders": [],
}

client = OpenAI()

df = pd.read_csv("orders.csv")
all_customers = [
    str(int(customer))
    for customer in df["CustomerID"].tolist()
    if not math.isnan(customer)
]


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
            {
                "role": "system",
                "content": '{"OrderID":"536365", "Intent":"TOTAL_ORDER_COST"}',
            },
            {"role": "user", "content": "total cost of all items in the order 536365"},
            {
                "role": "system",
                "content": '{"OrderID":"536365", "Intent":"TOTAL_ORDER_COST"}',
            },
            {"role": "user", "content": "Which items were ordered in 536364"},
            {
                "role": "system",
                "content": '{"OrderID":"536364", "Intent":"ORDER_ITEM_DETAILS"}',
            },
            {"role": "user", "content": "Can i cancel the order 458891"},
            {"role": "system", "content": '{"OrderID":"458891", "Intent":"CANCEL"}'},
            {
                "role": "user",
                "content": "How many items were ordered in Invoice 558420",
            },
            {
                "role": "system",
                "content": '{"OrderID":"558420", "Intent":"NUMBER_OF_ITEMS"}',
            },
            {"role": "user", "content": "Order ID 17850"},
            {"role": "system", "content": '{"OrderID":"17850", "Intent":"None"}'},
            {"role": "user", "content": "all products"},
            {"role": "system", "content": '{"OrderID":"None", "Intent":"None"}'},
            {"role": "user", "content": user_query},
        ],
        seed=42,
        n=1,
    )
    output = response.choices[0].message.content
    return json.loads(output)


def cancel_order(invoice_number):
    """Function to determine whether an order is eligible for cancellation.
    Eligibility criteria:
    1. Order should belong to the Customer ID provided as input
    2. Order should have been placed in the last 14 days from the date input
    3. Order should be a valid existing order
    """

    cancel = {}
    if invoice_number in CONTEXT_DATA["CancelledOrders"]:
        cancel["eligible"] = False
        cancel[
            "reason"
        ] = f"Order {invoice_number} already cancelled. Please try another Order ID"
        return cancel

    invoice_details = df.loc[df["InvoiceNo"] == invoice_number]
    if len(invoice_details) == 0:
        cancel["eligible"] = False
        cancel[
            "reason"
        ] = f"Sorry! We couldn't find order: {invoice_number}. Please try another Order ID"
        CONTEXT_DATA["CancelOrderId"] = None
        return cancel

    customerId = invoice_details.iloc[0]["CustomerID"]
    if not math.isnan(customerId):
        customerId = str(int(customerId))
    else:
        cancel["eligible"] = False
        cancel[
            "reason"
        ] = f"There is no information on the Customer ID for this order. Please try another Order ID"
        CONTEXT_DATA["CancelOrderId"] = None
        return cancel

    if customerId.strip() != customerid_input.value.strip():
        cancel["eligible"] = False
        cancel[
            "reason"
        ] = f"Sorry! The order {invoice_number} belongs to a different customer"
        CONTEXT_DATA["CancelOrderId"] = None
        return cancel

    try:
        invoice_date = invoice_details.iloc[0]["InvoiceDate"]
        date_object = datetime.datetime.strptime(
            invoice_date.split()[0], "%m/%d/%y"
        ).date()
        date_difference = date_picker.value - date_object
    except Exception as e:
        cancel["eligible"] = False
        cancel["reason"] = f"Failed to process Invoice date for order {invoice_number}"
        CONTEXT_DATA["CancelOrderId"] = None
        return cancel

    if date_difference.days <= 14:
        cancel["eligible"] = True
        CONTEXT_DATA["CancelOrderId"] = invoice_number
        return cancel
    else:
        cancel["eligible"] = False
        cancel["reason"] = (
            f"Order {invoice_number} not eligible for cancellation. "
            f"We can only cancel orders placed in the last 14 days"
        )
        CONTEXT_DATA["CancelOrderId"] = None
        return cancel


def customer_chatbot_agent(user_query, verbose=False):
    """An agent that can respond to customer's queries regarding orders"""

    global CONTEXT_DATA

    output = detect_order_number_and_intent(user_query)
    if verbose:
        print(output)

    if not isinstance(output, dict):
        return "We faced some issue processing your query. Please try again!"

    if "OrderID" not in output or "Intent" not in output:
        return (
            "Please provide a valid request. You need to "
            "enter CustomerID in the left sidebar if not done already. "
            "Please enter a valid OrderID that you need to cancel."
        )

    invoice_number = output["OrderID"]
    intent = output["Intent"]

    if verbose:
        print(f"OrderID: {invoice_number}, Intent: {intent}")

    if not customerid_input.value:
        return "Please provide your CustomerID first in the left sidebar"
    elif customerid_input.value not in all_customers:
        return "Please provide a valid CustomerID"

    # Check if user has requested for order cancellation and confirm the same
    if CONTEXT_DATA["CancelConfirmationPending"]:
        if "yes" in user_query.lower():
            msg = (
                f"Order {CONTEXT_DATA['CancelOrderId']} successfully cancelled. "
                f"Is there anything else we can help you with?"
            )
            CONTEXT_DATA["CancelledOrders"].append(CONTEXT_DATA["CancelOrderId"])
            CONTEXT_DATA["CancelOrderId"] = None
            CONTEXT_DATA["CancelConfirmationPending"] = False
            return msg
        else:
            CONTEXT_DATA["CancelConfirmationPending"] = False
            return "Order not cancelled. Is there anything else we can help you with?"

    if invoice_number == "None":
        return (
            "Please provide an Order ID along with the action you need to perform on the order. "
            "Note that we only support cancellations currently."
        )
    elif intent == "None":
        return (
            "Please provide more details regarding the action you want to take on the order. "
            "Currently we support order cancellations only."
        )

    if intent != "CANCEL":
        return (
            "We only support order cancellation requests. "
            "Please help us with the Order ID you want to cancel."
        )
    else:
        try:
            cancellation = cancel_order(invoice_number)
            if cancellation["eligible"]:
                CONTEXT_DATA["CancelConfirmationPending"] = True
                return "Please confirm that you want to cancel the order (Yes/No)"

            else:
                return cancellation["reason"]
        except Exception as e:
            if verbose:
                print(str(e))
            return "We faced some issues in cancelling your order. Please try again!"


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    return customer_chatbot_agent(contents)


chat_interface = pn.chat.ChatInterface(callback=callback, callback_exception="verbose")
chat_interface.send(
    "I am a customer chat assistant and I'll help you perform actions on your order!\n"
    "Please enter your customer ID and current date before further processing.\n\n"
    "You can deploy your own by signing up at https://ploomber.io",
    user="System",
    respond=False,
)

customerid_input = pn.widgets.TextInput(
    name="Customer ID", placeholder="Enter your Customer ID"
)
date_picker = pn.widgets.DatePicker(
    name="Today's Date", value=datetime.datetime(2011, 12, 9)
)


pn.template.FastListTemplate(
    title="Customer Chatbot",
    sidebar=[customerid_input, date_picker],
    main=[chat_interface],
).servable()
