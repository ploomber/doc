# About this application

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

## Key components in this application

1. `pipelinehelper.py`: This file contains the code for the pipeline. It uses the Haystack framework to build a RAG pipeline that can answer questions about orders. The pipeline is initialized with a document store that contains information about orders. The pipeline uses the document store to answer questions about orders.

2. `app.py`: This file contains the code for the API. It uses FastAPI to build an API that can answer questions about orders. The API is initialized with a pipeline that can answer questions about orders.

3. `Dockerfile`: This file contains the instructions for building a Docker image for this application.

4. `requirements.txt`: This file contains the Python dependencies for this application.