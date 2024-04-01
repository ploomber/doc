"""
Customer chatbot.

Input:
Users can submit queries by specifying a certain action that they want the chat assistant to perform
on a particular Order ID.
Answers to user's queries will be based on the Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

Response:
Currently the chat assistant can perform the following actions:
1. Get ID of all orders placed by customer
2. Allowing cancellation of a particular order if it has been placed
   in the last 14 days
3. Get specific order details
"""

import json
import datetime
import pandas as pd
import panel as pn
from openai import OpenAI

pn.extension("tabulator")

CANCELLATION_CONTEXT_DATA = {
    "CancelOrderId": None,
    "CancelConfirmationPending": False,
    "CancelledOrders": [],
}

client = OpenAI()

df = pd.read_csv("orders.csv")
df["CustomerID"] = df["CustomerID"].apply(
    lambda x: str(int(x)) if not pd.isna(x) else ""
)
all_customers = df["CustomerID"].tolist()


def detect_order_number_and_intent(user_query):
    """Function to detect Order ID (Invoice number) and intent in the
    user query"""

    system_prompt = f"""
        You're a system that determines the invoice number (order number) and the intent in the user query. 

        You need to return only the order number. If no invoice number or order number is found 
        return the string None.
        
        You need to return only the intent and no additional sentences.
        If relevant intent is not found then return the string None.

        Valid intents = ["CANCEL", "GET_ORDERS", "ORDER_ITEM_DETAILS"]
        
        You should return the response as a JSON.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Which items were ordered in 536364"},
            {
                "role": "system",
                "content": '{"OrderID":"536364", "Intent":"ORDER_ITEM_DETAILS"}',
            },
            {"role": "user", "content": "Can i cancel the order 458891"},
            {"role": "system", "content": '{"OrderID":"458891", "Intent":"CANCEL"}'},
            {"role": "user", "content": "Which orders have I placed"},
            {"role": "system", "content": '{"OrderID":"None", "Intent":"GET_ORDERS"}'},
            {"role": "user", "content": "Please get my orders"},
            {"role": "system", "content": '{"OrderID":"None", "Intent":"GET_ORDERS"}'},
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


def get_orders():
    """Function to fetch all orders of given customer"""

    customerId = customerid_input.value.strip()
    customer_orders = df.loc[df["CustomerID"] == customerId]
    order_ids = customer_orders["InvoiceNo"].unique().tolist()
    return ", ".join(order_ids)


def get_order_details(invoice_number):
    """Function to fetch order details"""

    order_details = df.loc[df["InvoiceNo"] == invoice_number]
    order_details = order_details.reset_index(drop=True)
    if len(order_details) == 0:
        return {
            "Found": False,
            "Reason": "This Order ID doesn't exist. Please input a valid order ID",
        }
    customerId = order_details.iloc[0]["CustomerID"]
    if not customerId:
        return {
            "Found": False,
            "Reason": "There is no information on the Customer  "
            "ID for this order. Please try another Order ID",
        }

    if customerId.strip() != customerid_input.value.strip():
        return {
            "Found": False,
            "Reason": "Sorry! The order "
            f"{invoice_number} belongs to a different customer",
        }
    return {"Found": True, "Data": order_details}


def create_cancellation_details(reason):
    cancel = {"eligible": False, "reason": reason}
    CANCELLATION_CONTEXT_DATA["CancelOrderId"] = None
    return cancel


def cancel_order(invoice_number):
    """Function to determine whether an order is eligible for cancellation.
    Eligibility criteria:
    1. Order should belong to the Customer ID provided as input
    2. Order should have been placed in the last 14 days from the date input
    3. Order should be a valid existing order
    """

    cancel = {}
    if invoice_number in CANCELLATION_CONTEXT_DATA["CancelledOrders"]:
        cancel["eligible"] = False
        cancel[
            "reason"
        ] = f"Order {invoice_number} already cancelled. Please try another Order ID"
        return cancel

    invoice_details = df.loc[df["InvoiceNo"] == invoice_number]
    if len(invoice_details) == 0:
        return create_cancellation_details(
            f"Sorry! We couldn't find order: "
            f"{invoice_number}. Please try another Order ID"
        )

    customerId = invoice_details.iloc[0]["CustomerID"]
    if not customerId:
        return create_cancellation_details(
            f"There is no information on the Customer "
            f"ID for this order. Please try another Order ID"
        )

    if customerId.strip() != customerid_input.value.strip():
        return create_cancellation_details(
            f"Sorry! The order " f"{invoice_number} belongs to a different customer"
        )

    try:
        invoice_date = invoice_details.iloc[0]["InvoiceDate"]
        date_object = datetime.datetime.strptime(
            invoice_date.split()[0], "%m/%d/%y"
        ).date()
        date_difference = date_picker.value - date_object
    except Exception:
        return create_cancellation_details(
            f"Failed to process " f"Invoice date for order {invoice_number}"
        )

    if 14 >= date_difference.days >= 0:
        cancel = {"eligible": True}
        CANCELLATION_CONTEXT_DATA["CancelOrderId"] = invoice_number
        return cancel
    else:
        return create_cancellation_details(
            f"Order {invoice_number} not eligible for cancellation. "
            f"We can only cancel orders placed in the last 14 days"
        )


def customer_chatbot_agent(user_query, verbose=False):
    """An agent that can respond to customer's queries regarding orders"""

    global CANCELLATION_CONTEXT_DATA

    output = detect_order_number_and_intent(user_query)
    if verbose:
        print(output)

    if not isinstance(output, dict):
        return "We faced some issue processing your query. Please try again!"

    if "OrderID" not in output or "Intent" not in output:
        return (
            "Please provide a valid request. You need to "
            "enter CustomerID in the left sidebar if not done already. "
        )

    invoice_number = output["OrderID"]
    intent = output["Intent"]

    if verbose:
        print(f"OrderID: {invoice_number}, Intent: {intent}")

    if not customerid_input.value:
        customerid_input.value = "15574"
    elif customerid_input.value not in all_customers:
        return "Please provide a valid CustomerID"

    # Check if user has requested for order cancellation and confirm the same
    if CANCELLATION_CONTEXT_DATA["CancelConfirmationPending"]:
        if "yes" in user_query.lower():
            msg = (
                f"Order {CANCELLATION_CONTEXT_DATA['CancelOrderId']} successfully cancelled. "
                f"Is there anything else we can help you with?"
            )
            CANCELLATION_CONTEXT_DATA["CancelledOrders"].append(
                CANCELLATION_CONTEXT_DATA["CancelOrderId"]
            )
            CANCELLATION_CONTEXT_DATA["CancelOrderId"] = None
            CANCELLATION_CONTEXT_DATA["CancelConfirmationPending"] = False
            return msg
        else:
            CANCELLATION_CONTEXT_DATA["CancelConfirmationPending"] = False
            return "Order not cancelled. Is there anything else we can help you with?"

    if intent == "None":
        return (
            "Please provide the action you need to perform. We support:\n"
            "1. Get all orders\n"
            "2. Get specific order details\n"
            "3. Cancel an order"
        )
    if invoice_number == "None" and intent != "GET_ORDERS":
        return "Please provide an Order ID along with the action you need to perform on the order."

    if intent == "CANCEL":
        try:
            cancellation = cancel_order(invoice_number)
            if cancellation["eligible"]:
                CANCELLATION_CONTEXT_DATA["CancelConfirmationPending"] = True
                return "Please confirm that you want to cancel the order (Yes/No)"

            else:
                return cancellation["reason"]
        except Exception as e:
            if verbose:
                print(str(e))
            return "We faced some issues in cancelling your order. Please try again!"

    elif intent == "GET_ORDERS":
        all_orders = get_orders()
        return f"Here are the orders placed by you: {all_orders}"

    elif intent == "ORDER_ITEM_DETAILS":
        order_details = get_order_details(invoice_number)
        if order_details["Found"]:
            table = pn.widgets.Tabulator(order_details["Data"])
            if invoice_number in CANCELLATION_CONTEXT_DATA["CancelledOrders"]:
                return pn.Column(
                    pn.widgets.StaticText(
                        name="Note", value="This order has been cancelled"
                    ),
                    table,
                )
            return table
        else:
            return order_details["Reason"]

    else:
        return (
            "Invalid request. We support the below actions:\n1. "
            "Order cancellation\n2. Get orders\n3. Get order details"
        )


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


app_description = pn.pane.Markdown(
    """
This app allows users to perform actions on their [orders](https://archive.ics.uci.edu/dataset/352/online+retail).

1. Input **Customer ID**, default provided.
2. Input **Today's Date**, default provided. Only orders in the past 14 days can be cancelled.
3. Users can enter queries like:
   a. Which orders have I placed
   b. I want to know details of order 556878
   c. Please cancel Order ID 556878
4. CustomerID *15574* has the following orders (using *2011-06-20* as Today's Date):
   a. 556878 (5 days old, you can cancel this one)
   b. 539215 (182 days old, you cannot cancel)
   c. 536796 (200 days old, you cannot cancel)
   In order to cancel 539215 set date as 2010-12-18. To cancel 536796 try setting date as 2010-12-05.
""",
    margin=(0, 0, 10, 0),
)

customerid_input = pn.widgets.TextInput(name="Customer ID", placeholder="15574")
date_picker = pn.widgets.DatePicker(
    name="Today's Date", value=datetime.datetime(2011, 6, 20)
)


pn.template.FastListTemplate(
    title="Customer Chatbot",
    sidebar=[app_description, customerid_input, date_picker],
    main=[chat_interface],
    sidebar_width=400,
).servable()
