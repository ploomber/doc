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

            This API uses the  Haystack (https://haystack.deepset.ai/overview/intro) framework to build a 
            Retrieval Augmented Generation (RAG) pipeline that can answer questions about orders. 
            The pipeline is initialized with a document store that contains information about orders.
            The pipeline uses the document store to answer questions about orders.

            The API is built with FastAPI (https://fastapi.tiangolo.com/), a modern, fast (high-performance),
            web framework for building APIs with Python 3.6+ based on standard Python type hints.

            It is deployed on  Ploomber Cloud (https://ploomber.io/), a platform for building and deploying
            Python data and AI-based apps.

            ## Sample data

            | invoiceno	| stockcode	| description                       | quantity  |invoicedate     |unitprice | customerid| country         |
            |-----------|-----------|-----------------------------------|-----------|----------------|-----------|----------|-----------------|
        	|536365	    |85123A	    |WHITE HANGING HEART T-LIGHT HOLDER	| 6         | 12/1/2010 8:26 | 2.55	     | 17850.0	| United Kingdom  |
        	|536365	    |71053	    |WHITE METAL LANTERN            	| 6	        | 12/1/2010 8:26 | 3.39      | 17850.0	| United Kingdom  |
        	|536365	    |84406B	    |CREAM CUPID HEARTS COAT HANGER	    | 8	        | 12/1/2010 8:26 | 2.75	     | 17850.0	| United Kingdom  |
        	|536365	    |84029G     |KNITTED UNION FLAG HOT WATER BOTTLE| 6	        | 12/1/2010 8:26 | 3.39	     | 17850.0	| United Kingdom  |
        	|536365	    |84029E	    |RED WOOLLY HOTTIE WHITE HEART      | 6	        | 12/1/2010 8:26 | 3.39	     | 17850.0  | United Kingdom  |

            ## Sample questions

            * What is the total cost for order with invoice number 536365?
            * What were the items in order 536365?
            * How many items were in order 536365?
            * What was the date of order 536365?

            Order numbers you can try: '536365', '536366', '536367', '536368', '536369', '536370'
            Orders that contain information on cancellations: 'C536379', 'C536383', 'C536391'
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
