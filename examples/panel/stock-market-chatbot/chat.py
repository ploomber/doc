from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import json 

load_dotenv(".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_name = "gpt-3.5-turbo"


def as_json(obj):
    """
    Convert an object to a JSON serializable dictionary
    """
    return json.loads(obj.model_dump_json())

def create_thread():
    """
    Create a new thread
    """
    return client.beta.threads.create()

def add_message_to_thread(thread_id, message_content):
    return client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_content
    )

def run_assistant(thread_id, assistant_id):
    """
    Run an assistant on a thread
    """
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

def wait_on_run(run, thread):
    """
    Wait for a run to complete - assistant runs are queued by default, 
    we need to wait for them to complete before we can retrieve the messages
    """
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
    
def start_assistant(query):
    """
    Start an assistant to search for repositories on GitHub
    """
    
    system_message = "You are an expert data and stock market analyst whose only job is to\
        translate natural language questions into SQL queries that can be executed\
            against a DuckDB instance containing stock market data."
    
    assistant = client.beta.assistants.create(
    name="Stock market assistant",
    instructions=system_message,
    model=model_name,
)
    thread = create_thread()
    add_message_to_thread(thread.id, query)
    queued_run = run_assistant(thread.id, assistant.id)
    run = wait_on_run(queued_run, thread)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return run, messages

def sql_query_generator(query):
    run, raw_response = start_assistant(query)
    messages = as_json(raw_response)
    # Obtain response from the assistant and log it
    interpretation = messages['data'][0]['content'][0]['text']['value']

    return interpretation