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
from rag import vectorize_json, save_index
from bs4 import BeautifulSoup

last_action = {"type": None, "data": None}
# Load environment variables from a .env file
load_dotenv(".env")
# Set the WANDB_API_KEY environment variable
os.environ["WANDB_API_KEY"] = os.getenv("WANDB_API_KEY")
# Set the GITHUB_TOKEN environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

# start a wandb run to log to
wandb.init(project=os.getenv("WANDB_PROJECT"), 
           entity=os.getenv("WANDB_ENTITY"))

# Initialize the OpenAI client and create an assistant
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_name = "gpt-3.5-turbo"

search_results = {}

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
        time.sleep(0.00001)
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
        # elif "repos" in url and "readme" in url:
        #     document_store = run_indexing_pipeline(url)
        #     return run_retrieval_pipeline(document_store, query)
        else:
            return "URL matched but did not fit expected patterns."
    else:
        return interpretation

def search_github_repositories(url):
    """
    This function takes a url and uses the GitHub API to search for repositories
    sorted by the number of stars
    """
    global search_results  
    search_results.clear()

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

            for repo in top_repos:
                repo_name = repo['name']
                search_results[repo_name] = {
                    'full_name': repo['full_name'],
                    'html_url': repo['html_url'],
                    'description': repo['description'],
                    'stargazers_count': repo['stargazers_count']
                }

            repo_list += "\n".join([f"- <a href='{repo['html_url']}' target='_blank'>{repo['html_url'].split('/')[-1]}</a>: {repo['description']} - Stargazer count ⭐: {repo['stargazers_count']}" for repo in top_repos])
            return Markdown(repo_list)
        else:
            repo_list = "Here are the repositories related to your search:\n"
            repos = json_response['items']

            for repo in repos:
                repo_name = repo['name']
                search_results[repo_name] = {
                    'full_name': repo['full_name'],
                    'html_url': repo['html_url'],
                    'description': repo['description'],
                    'stargazers_count': repo['stargazers_count']
                }

            repo_list += "\n".join([f"- <a href='{repo['html_url']}' target='_blank'>{repo['html_url'].split('/')[-1]}</a>: '{repo['description']}' - Stargazer count ⭐: {repo['stargazers_count']}" for repo in repos])
            return Markdown(repo_list)
            
    else:
        return "I am sorry, I wasn't able to retrieve the repositories. \
            Please tell me a topic for which you want to find repositories.\
            If the problem persists and I cannot connect to the GitHub API,\
            please try again later."


def fetch_readme_details(url):
    """
    Fetch the README.md file from a specific repository using GitHub API with authorization,
    assuming the content is in HTML format, and extract only the text content.
    """
    headers = {
        "Accept": "application/vnd.github.VERSION.html",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove all script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()  # Remove these elements

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
    else:
        print(f"Failed to fetch README.md: {response.status_code}")
        return None
    
def summarize_readme(readme_content):
    """
    Use OpenAI API to generate a summary of the README content.
    """
    # Ensure the content is not too large for the API request
    if len(readme_content) > 4000:
        readme_content = readme_content[:4000] + "... (Content truncated for summarization)"
    prompt=f"Summarize this README content:\n\n{readme_content}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        
        messages=[
            {"role": "system", "content": "Your task is to review the README content and provide a summary."},
            {"role": "user", "content": "Can you summarize this README content?"},
            {"role": "assistant", "content": prompt},
            ]
    )
    answer = response.choices[0].message.content
    return answer 

def preprocess_readme_content(content):
    # Remove Markdown tables: Look for lines starting with pipe characters as simple table indicators
    content = re.sub(r'\n\|.*\|\n', '\n', content)
    
    # Remove URLs
    content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)

    # Convert line breaks to spaces
    content = content.replace('\n', ' ')

    # Remove special characters, except periods and commas
    content = re.sub(r'[^a-zA-Z0-9 .,]', ' ', content)

    # Replace multiple spaces with a single space
    content = re.sub(r'\s+', ' ', content)

    return content

def handle_detailed_repository_query(query):
    """
    Handle detailed queries for a specific repository.
    """
    global search_results

    # Extract the repository name from the query
    match = re.search(r"tell me more about ([\w-]+)", query, re.IGNORECASE)
    if not match:
        return "Please start your questions with 'tell me more about <name or url of repo>."

    repo_name = match.group(1)  # The name of the repository
    if repo_name in search_results:
        repo_full_name = search_results[repo_name]['full_name']
        readme_url = f"https://api.github.com/repos/{repo_full_name}/readme"
        raw_readme_content = fetch_readme_details(readme_url)
        cleaned_readme_content = preprocess_readme_content(raw_readme_content)
        return summarize_readme(cleaned_readme_content)
    else:
        return f"I couldn't find details about '{repo_name}'. Please make sure the repository name is correct or perform another search."


def callback(input_text, user, instance: pn.chat.ChatInterface):
    """
    This function is called when the user sends a message
    """
    
    if "tell me more about" in input_text:
        return handle_detailed_repository_query(input_text)
    else:
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
