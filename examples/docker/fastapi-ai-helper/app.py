from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn

from pipelinehelper import (read_and_clean_csv, 
                            generate_haystack_documents, 
                            populate_document_store, 
                            initialize_pipeline)

# Load environment variables
load_dotenv(".env")

# Initialize FastAPI app
app = FastAPI()

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
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
