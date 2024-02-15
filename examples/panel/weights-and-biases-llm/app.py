import panel as pn
from openai import OpenAI
from wandb.sdk.data_types.trace_tree import Trace
from dotenv import load_dotenv
import os
import wandb
import datetime
import requests
import time
import json

# load the .env file
load_dotenv(".env")
# Set the WANDB_API_KEY environment variable
os.environ["WANDB_API_KEY"] = os.getenv("WANDB_API_KEY")

# start a wandb run to log to
wandb.init(project=os.getenv("WANDB_PROJECT"), 
           entity=os.getenv("WANDB_ENTITY"))

# Initialize the OpenAI client and create an assistant
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
    
    system_message = "You are a helpful assistant who translates natural language questions and forms a url that can be used\
        to search through repositories on GitHub through their API\
        For example, if a user asks for repositories for llm monitoring, you will form a query as follows\
        https://api.github.com/search/repositories?q=llm+monitoring"
    
    assistant = client.beta.assistants.create(
    name="GitHub repository searcher",
    instructions=system_message,
    model=model_name,
)
    thread = create_thread()
    add_message_to_thread(thread.id, query)
    queued_run = run_assistant(thread.id, assistant.id)
    run = wait_on_run(queued_run, thread)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return run, messages
 
def trace_log(status, status_message, token_usage, \
              start_time_ms, end_time_ms, query, \
                response_text, json_run, model_name):

    root_span = Trace(
            name="root_span",
            kind="tool",  # kind can be "llm", "chain", "agent" or "tool"
            status_code=status,
            status_message=status_message,
            metadata={
                "token_usage": token_usage,
                "model_name": model_name,
            },
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            inputs={"system_prompt": json_run['instructions'], "query": query},
            outputs={"response": response_text},
        )
    
    return root_span


def github_url_generator(query):
    """
    This function takes a query in natural language
    and returns a url that can be used to search through 
    repositories on GitHub
    """
    try:

        # start a span to trace the assistant
        start_time_ms = datetime.datetime.now().timestamp() * 1000
        run, raw_response = start_assistant(query)
        messages = as_json(raw_response)
        json_run = as_json(run)
        end_time_ms = round(
                    datetime.datetime.now().timestamp() * 1000
            ) 
        # Obtain response from the assistant and log it
        interpretation = messages['data'][0]['content'][0]['text']['value']
        status = "success"
        status_message = (None,)
        response_text = interpretation
        token_usage = json_run['usage']

        root_span = trace_log(status, status_message, token_usage, \
                            start_time_ms, end_time_ms, query, \
                                response_text, json_run, model_name)

        # log the span to wandb
        root_span.log(name="openai_trace")


    except Exception as e:
        end_time_ms = round(
            datetime.datetime.now().timestamp() * 1000
        )  # logged in milliseconds
        status = "error"
        status_message = str(e)
        response_text = ""
        token_usage = {}

        root_span = trace_log(status, status_message, token_usage, \
                            start_time_ms, end_time_ms, query, \
                                response_text, json_run, model_name)

        # log the span to wandb
        root_span.log(name="openai_trace")
        
    return interpretation

def search_github_repositories(url):
    url = url
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['items']
    else:
        return []

def callback(input_text, user, instance: pn.chat.ChatInterface):
    
    return github_url_generator(input_text)



chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "Hello, I can help you find repositories on GitHub. What are you looking for?",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="GitHub Repository Searcher",
    main=[chat_interface],
).servable()
