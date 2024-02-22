import panel as pn
from openai import OpenAI
from wandb.sdk.data_types.trace_tree import Trace
import wandb
import datetime
import requests
import time
import json
import re
import os 
from IPython.display import Markdown
from dotenv import load_dotenv

last_action = {"type": None, "data": None}
# Load environment variables from a .env file
load_dotenv(".env")
# Set the WANDB_API_KEY environment variable
os.environ["WANDB_API_KEY"] = os.getenv("WANDB_API_KEY")
# Set the GITHUB_TOKEN environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

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
    
    system_message = "You are a helpful assistant whose only job is to\
        translates natural language questions and forms a url that can be used\
        to search through repositories on GitHub through their API\
        For example, if a user asks for repositories for llm monitoring, you will form a query as follows\
        https://api.github.com/search/repositories?q=llm+monitoring\
        \
        If a user asks you to tell them more about a specific repository, the user should specify the complete GitHub URL \
        For example, if a user asks 'tell me more about https://github.com/WenjieDu/PyPOTS', you will form a query as follows \
        https://api.github.com/repos/WenjieDu/PyPOTS/readme\
        Any inquiries outside of this should be responded with \
        'I can help you find GitHub repositories only. Tell me a topic you are interested in.'"
    
    assistant = client.beta.assistants.create(
    name="GitHub repository searcher.",
    instructions=system_message,
    model=model_name,
)
    thread = create_thread()
    add_message_to_thread(thread.id, query)
    queued_run = run_assistant(thread.id, assistant.id)
    run = wait_on_run(queued_run, thread)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return run, messages
 
def trace_log(status, status_message, token_usage, start_time_ms, end_time_ms, query, response_text, json_run, model_name):
    """
    This function logs a span to Weights and Biases
    """
    system_prompt = json_run.get('instructions', 'Unknown instructions')  # Use a default value if 'instructions' key is not found

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
            inputs={"system_prompt": system_prompt, "query": query},
            outputs={"response": response_text},
        )
    
    return root_span


def github_url_generator(query):
    """
    This function takes a query in natural language
    and returns a url that can be used to search through 
    repositories on GitHub

    This function also has Weights and Biases tracing enabled
    """
    json_run = {}
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
        json_run = {}
        instructions = ""

        root_span = trace_log(status, status_message, token_usage, \
                            start_time_ms, end_time_ms, query, \
                                response_text, json_run, model_name)

        # log the span to wandb
        root_span.log(name="openai_trace")

        return "I am sorry, our LLM is currently down. Please try again later."

     # Updated regular expression to match either search repositories or a specific repo's README
    url_pattern = r"(https://api\.github\.com/search/repositories\?.+)|(https://api\.github\.com/repos/.+?/.+?/readme)"
    match = re.search(url_pattern, interpretation)

    if match:
        url = match.group()
        # Determine which pattern was matched to decide on the action
        if "search/repositories" in url:
            return search_github_repositories(url)
        elif "repos" in url and "readme" in url:
            # Assuming you have a function to process direct README requests
            return fetch_readme_details(url)
        else:
            return "URL matched but did not fit expected patterns."
    else:
        return interpretation

def search_github_repositories(url):
    """
    This function takes a url and uses the GitHub API to search for repositories
    sorted by the number of stars
    """

    url += "&sort=stars&order=desc"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    json_response = response.json()

    if response.status_code == 200:
        if len(json_response['items']) < 1:
            return "No repositories found for the given search criteria.\
                Please try a different search."
        if len(json_response['items']) > 15:
            repo_list = "Here are top 15 repositories (by number of stars) related to your search:\n"
            top_repos = json_response['items'][:15]  # Get the top 15 repositories
            repo_list += "\n".join([f"- <a href='{repo['html_url']}' target='_blank'>{repo['html_url'].split('/')[-1]}</a>: {repo['description']} - Stargazer count ⭐: {repo['stargazers_count']}" for repo in top_repos])
            return Markdown(repo_list)
        else:
            repo_list = "Here are the repositories related to your search:\n"
            repos = json_response['items']
            repo_list += "\n".join([f"- <a href='{repo['html_url']}' target='_blank'>{repo['html_url'].split('/')[-1]}</a>: '{repo['description']}' - Stargazer count ⭐: {repo['stargazers_count']}" for repo in repos])
            return Markdown(repo_list)
            
    else:
        return "I am sorry, I wasn't able to retrieve the repositories. \
            Please tell me a topic for which you want to find repositories.\
            If the problem persists and I cannot connect to the GitHub API,\
            please try again later."

def fetch_readme_details(url):
    """
    Fetch the README.md file from a specific repository using GitHub API with authorization.
    
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        readme_data = response.json()
        # Fetch the raw README content using the download_url from the README metadata
        readme_content_response = requests.get(readme_data['download_url'], headers=headers)
        if readme_content_response.status_code == 200:
            return readme_content_response.text
        else:
            print(f"Failed to fetch raw README content: {readme_content_response.status_code}")
            return None
    else:
        print(f"Failed to fetch README.md: {response.status_code}")
        return None


def summarize_readme(readme_content):
    """
    Use OpenAI to summarize the README.md content.
    """
    response = client.chat.completions.create(
        model=model_name,
        prompt=f"Summarize this README.md content:\n\n{readme_content}",
        temperature=0.7,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()




def callback(input_text, user, instance: pn.chat.ChatInterface):
    """
    This function is called when the user sends a message
    """
    
    return github_url_generator(input_text)


chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "Hello 😊 I am an OpenAI-powered assistant. \
        I can help you find repositories on GitHub. \
        Tell me a topic and I will use the GitHub API to suggest a few \
        repositories for you. I can also provide more information about a specific repository. \
        You can provide the complete URL to a repository and I can provide a high level overview of its purpose.\
        \nFor example, you can ask me 'tell me more about https://github.com/ploomber/jupysql' or 'show me repositories for llm monitoring'.",
    user="System",
    respond=False,
)

pn.template.MaterialTemplate(
    title="<h4>GitHub Repository Searcher - <a href='https://ploomber.io/' target='_blank'> Hosted on Ploomber Cloud 🚀</a></h4>",
    logo="./images/logo-nb.png",
    main=[chat_interface],
).servable()
