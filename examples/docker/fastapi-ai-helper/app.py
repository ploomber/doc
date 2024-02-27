from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn

from pipelinehelper import (read_and_clean_csv, 
                            generate_haystack_documents, 
                            populate_document_store, 
                            initialize_pipeline)

description = """
This is an LLM-based API with a focus on helping you answer questions about orders. 🚀

## How it works

This API uses the  [Haystack](https://haystack.deepset.ai/overview/intro) framework to build a 
Retrieval Augmented Generation (RAG) pipeline that can answer questions about orders. 
The pipeline is initialized with a document store that contains information about orders.
The pipeline uses the document store to answer questions about orders.

The API is built with [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance),
web framework for building APIs with Python 3.6+ based on standard Python type hints.

It is deployed on [Ploomber Cloud](https://ploomber.io/), a platform for building and deploying
Python data and AI-based apps.

## Sample data

Data source: UCI Machine Learning Repository "Online Retail" dataset

Link: https://archive.ics.uci.edu/dataset/352/online+retail

| invoiceno	| stockcode	| description                       | quantity  |invoicedate     |unitprice  | customerid| country         |
|-----------|-----------|-----------------------------------|-----------|----------------|-----------|----------|-----------------|
|536365	    |85123A	    |WHITE HANGING HEART T-LIGHT HOLDER	| 6         | 12/1/2010 8:26 | 2.55	     | 17850	| United Kingdom  |
|536367     |84879      |ASSORTED COLOUR BIRD ORNAMENT      | 32        | 12/1/2010 8:34 | 1.69      | 13047    | United Kingdom  |
|536381     |47580      |TEA TIME DES TEA COSY              | 2         | 12/1/2010 9:41 | 2.55      | 15311    | United Kingdom  |
|536858     |22326      |ROUND SNACK BOXES SET OF4 WOODLAND | 30        | 12/3/2010 10:36| 2.95      | 13520    | Switzerland     |
|537463     |22961      |JAM MAKING SET PRINTED             | 12        | 12/7/2010 10:08| 1.45      | 12681    | France          |

## Sample questions

* What is the total cost for order with invoice number 537463? 
* What were the items in order 536365?
* How many items were in order 536858?
* Can I still cancel order with invoice number 536365? 

Order numbers you can try: '536365', '536366', '536367', '536368', '536369', '536370'
Orders that contain information on cancellations: 'C536379', 'C536383', 'C536391'

## Using the curl command

For example, for the question `What were the items in order 536365?` you can run
the following curl command:

```bash
curl -X 'POST'
    'https://calm-violet-6179.ploomberapp.io/query'
    -H 'accept: application/json'
    -H 'Content-Type: application/json'
    -d '{
    "query": "What were the items in order 536365?"
    }'
```
This yields a JSON object with an answer key:

```bash
{
    "answer": "The items in order 536365 were:
                1. WHITE METAL LANTERN
                2. SET 7 BABUSHKA NESTING BOXES
                3. WHITE HANGING HEART T-LIGHT HOLDER
                4. CREAM CUPID HEARTS COAT HANGER
                5. RED WOOLLY HOTTIE WHITE HEART.
                6. GLASS STAR FROSTED T-LIGHT HOLDER
                7. KNITTED UNION FLAG HOT WATER BOTTLE"
    }
``` 

Similarly, for `What is the total cost for order with invoice number 537463?` you can run

```bash
curl -X 'POST'
    'https://calm-violet-6179.ploomberapp.io/query'
    -H 'accept: application/json'
    -H 'Content-Type: application/json'
    -d '{
    "query": "What is the total cost for order with invoice number 537463?"
    }'
```

This yields a JSON object with an answer key:

```bash
{
  "answer": "The total cost for order with invoice number 537463 is calculated as follows:
  - STRAWBERRY LUNCH BOX WITH CUTLERY: 6 * 2.55 = 15.3
  - LUNCH BOX WITH CUTLERY RETROSPOT: 6 * 2.55 = 15.3
  - POSTAGE: 4 * 18.0 = 72.0
  - DOORMAT RESPECTABLE HOUSE: 2 * 7.95 = 15.9
  - TABLECLOTH RED APPLES DESIGN: 4 * 8.5 = 34.0
  - GUMBALL COAT RACK: 36 * 2.1 = 75.6
  - WOODLAND STICKERS: 12 * 0.85 = 10.2
  - IVORY DINER WALL CLOCK: 2 * 8.5 = 17.0
  - RED RETROSPOT CUP: 16 * 0.85 = 13.6
  - WOODLAND CHARLOTTE BAG: 10 * 0.85 = 8.5
  
  Adding all these up, the total cost for order with invoice number 537463 is 15.3 + 15.3 + 72.0 + 15.9 + 34.0 + 75.6 + 10.2 + 17.0 + 13.6 + 8.5 = 277.4."
}
```

"""

# Load environment variables
load_dotenv(".env")

# Initialize FastAPI app
app = FastAPI(description=description)

# Define Pydantic models
class QueryModel(BaseModel):
    query: str

class ResponseModel(BaseModel):
    answer: str

# Load and prepare the pipeline
openai_key = os.getenv("OPENAI_KEY")
df_dict = read_and_clean_csv("data.csv")
haystack_documents = generate_haystack_documents(df_dict=df_dict)
document_store = populate_document_store(haystack_documents=haystack_documents)
prediction_pipeline = initialize_pipeline(document_store=document_store, openai_key=openai_key)

@app.post("/query", response_model=ResponseModel)
async def query_sales_data(query_model: QueryModel):
    try:
        query = query_model.query
        result = prediction_pipeline.run(data={"retriever": {"query": query}, 
                                               "prompt_builder": {"query": query},
                                               })
        return {"answer": result['generator']['replies'][0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Haystack AI Sales Query API"}

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=80)
