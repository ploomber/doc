from pipelinehelper import (read_and_clean_csv, 
                            generate_haystack_documents, 
                            populate_document_store, 
                            initialize_pipeline)
from dotenv import load_dotenv
import os
import pandas as pd

def get_items_from_answer(prediction_pipeline, order_number):
    """
    This function sets up the LLM response part of the test

    Args:
        prediction_pipeline (Pipeline): Prediction pipeline.
        order_number (str): Order number.

    Returns:
        items (list): List of tuples containing the item description and quantity.
    """

    query = f"Items for order with invoice number {order_number}"
    result = prediction_pipeline.run(data={"retriever": {"query": query}, 
                                        "prompt_builder": {"query": query},
                                        })
    final_answer= result['generator']['replies'][0]

    items = []
    for line in final_answer.strip().split("\n"):
        if "Item" in line:
            item_name = line.split(":")[1].strip().split(", ")[0]
            quantity = line.split(":")[2].strip()
            items.append((item_name, quantity))
    return items

def test_answers_against_ground_truth(test_df, items):
    """
    This function tests the LLM response against the ground truth

    Args:
        test_df (DataFrame): DataFrame containing the ground truth.
        items (list): List of tuples containing the item description and quantity.

    Returns:
        fail_flags (list): List of tuples containing the item description and quantity 
        that were not found.
    """
    
    fail_flags = []
    total_quantity_flag = False
    for item, quantity in items:
        if not test_df[(test_df['description'] == item) & (test_df['quantity'] == int(quantity))].empty:
            pass
        else:
            fail_flags.append((item, quantity))

    if len(fail_flags) == 0  & len(items)==test_df.shape[0]:
        print("All items found!")
        total_quantity_flag = True
    else:
        print("The following items were not found:")
        print(fail_flags)
        print("Or there are items in the dataframe the llm didn't identify")
        total_quantity_flag = False
    
    return fail_flags, total_quantity_flag


if __name__ == "__main__":
    # Load environment variables
    load_dotenv(".env")
    openai_key = os.getenv("OPENAI_KEY")
    df_dict = read_and_clean_csv("data.csv")
    haystack_documents = generate_haystack_documents(df_dict=df_dict)
    document_store = populate_document_store(haystack_documents=haystack_documents)
    prediction_pipeline = initialize_pipeline(document_store=document_store, openai_key=openai_key)

    df = pd.read_csv("data.csv")


    # Perform test
    results = []
    for i in range(100):
        test_llm = get_items_from_answer(prediction_pipeline, "536365")
        test_df = df[df['invoiceno'] == "536365"]

        test_result = test_answers_against_ground_truth(test_df, test_llm)
        results.append(test_result)