import pandas as pd

from haystack.dataclasses import Document
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import GPTGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever

def read_and_clean_csv(customer_data):
    """
    Read and clean the csv file. This function removes NaN values from the CustomerID column, 
    and renames the columns to all lower case. It returns a dictionary of the dataframe.

    Args:
        customer_data (str): Path to the csv file.

    Returns:
        df_dict (dict): Dictionary of the dataframe.
    """
        
    try:
        # Source https://www.kaggle.com/datasets/carrie1/ecommerce-data?resource=download
        df = pd.read_csv(customer_data, encoding='latin1')

        # Drop rows with empty CustomerID
        df.dropna(subset=['CustomerID'], inplace=True)

        # rename columns to all lower case
        df.columns = [x.lower() for x in df.columns]

        # Save df to dict
        df_dict = df.to_dict("records")

        return df_dict
    
    except Exception as e:
        print("Unable to read file due to:", e)
        return pd.DataFrame()

def generate_haystack_documents(df_dict):
    """
    Generate a list of Haystack documents from a dataframe.

    Args:
        df_dict (dict): Dictionary of the dataframe.

    Returns:
        haystack_documents (list): List of Haystack documents.
    """
    try:
        haystack_documents = []

        # Create a list of Haystack documents
        for i in range(len(df_dict)):
            content_str = f"Name of item purchased: {df_dict[i]['description']} \
                \nQuantity purchased: {df_dict[i]['quantity']} \
                \nPrice of item: {df_dict[i]['unitprice']} \
                \nDate of purchase: {df_dict[i]['invoicedate']} \
                \nCountry of purchase: {df_dict[i]['country']} \
                \nCustomer ID: {df_dict[i]['customerid']} \
                \nInvoice Number: {df_dict[i]['invoiceno']} \
                \nStock Code: {df_dict[i]['stockcode']}" ,
            haystack_documents.append(Document(
                content=content_str[0],
                id = f"ZOOA{str(1000000 + i)}",
                meta={
                    "invoiceno": df_dict[i]["invoiceno"],
                    "stockcode": df_dict[i]["stockcode"],
                    "description": df_dict[i]["description"],
                    "quantity": df_dict[i]["quantity"],
                    "invoicedate": df_dict[i]["invoicedate"],
                    "unitprice": df_dict[i]["unitprice"],
                    "customerid": df_dict[i]["customerid"],
                    "country": df_dict[i]["country"],
                },
            ))

        return haystack_documents
    
    except Exception as e:
        print("Unable to generate Haystack documents due to:", e)
        return []

def populate_document_store(haystack_documents):
    """
    Populate the document store with the Haystack documents.

    Args:
        haystack_documents (list): List of Haystack documents.
    """
    try:
        document_store = InMemoryDocumentStore(bm25_algorithm="BM25Plus")
        document_store.write_documents(documents=haystack_documents)
        return document_store
    
    except Exception as e:
        print("Unable to populate document store due to:", e)
        document_store = InMemoryDocumentStore(bm25_algorithm="BM25Plus")
        return document_store

def initialize_pipeline(document_store, openai_key):
    """
    Initialize the pipeline for the AI helper.

    Args:
        document_store (DocumentStore): Populated Haystack document store.
        openai_key (str): OpenAI API key.

    Returns:
        prediction_pipeline (Pipeline): Prediction pipeline.

    """

    try:
        prompt_template = """
        You are an expert data analyst who helps customers and employees with 
        their questions about purchases and products.
        You use the information provided in the documents to answer the questions.
        You can answer the following types of questions:
        Questions regarding the order: please ask the user to give you the invoice number.
        Questions regarding the product: please ask the user to give you the stock code.
        Questions regarding purchases made on a given day: please ask the user to give you the date of purchase.
        If you are asked to calculate the total price of a purchase, please ask the user to give you the invoice number and add the total price of the items in the purchase.
        If you are asked to calculate the total number of items for a purchase, please ask the user to give you the invoice number and add the total number of items in the purchase.
        If the documents do not contain the answer to the question, say that ‘Answer is unknown.’
        Context:
        {% for doc in documents %}
            Purchase information: {{ doc.content }} 
            Invoice Number: {{ doc.meta['invoiceno'] }} 
            Stock Code: {{doc.meta['stockcode']}}
            Quantity purchased: {{doc.meta['quantity']}}
            Date of purchase: {{doc.meta['invoicedate']}}
            Price per item: {{doc.meta['unitprice']}} \n
        {% endfor %};
        Question: {{query}}
        \n Answer:
        """
        prompt_builder = PromptBuilder(prompt_template)
        retriever = InMemoryBM25Retriever(document_store=document_store)
        ############################################
        llm = GPTGenerator(api_key=openai_key, 
                        generation_kwargs={"temperature": 0},
                        model='gpt-4')

        prediction_pipeline = Pipeline()
        prediction_pipeline.add_component("retriever", retriever)
        prediction_pipeline.add_component("prompt_builder", prompt_builder)
        prediction_pipeline.add_component("generator", llm)

        prediction_pipeline.connect("retriever.documents", "prompt_builder.documents")
        prediction_pipeline.connect("prompt_builder", "generator")

        return prediction_pipeline
    
    except Exception as e:
        print("Unable to initialize pipeline due to:", e)
        return None