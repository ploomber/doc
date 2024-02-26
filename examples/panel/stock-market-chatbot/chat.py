from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import json 
import duckdb

load_dotenv(".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_name = "gpt-3.5-turbo"
db_file = "stockdata.duckdb"

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
    
def start_assistant(query, ticker, start_date, end_date):
    """
    Start an assistant to search for repositories on GitHub
    """
    
    system_message = "You are an expert data and stock market analyst whose only job is to\
                        translate natural language questions into SQL queries that can be executed\
                        against a DuckDB instance containing stock market data.\
                        Your responses are correct,acurate and lack special characters.\
                        The table name corresponds to the symbol. These are the field names:\
                        'Date'	'Open'	'High'	'Low'	'Close'	'Adj Close'	'Volume'\
                        You will be given a ticker symbol, start date, end date and query\
                        Translate this natural language question into an SQL query : {query}.\
                        \
                        For example,if you are asked about all data on Apple (aapl) stock,\
                        the correct query would be :\
                            SELECT * \
                            FROM aapl"
    
    assistant = client.beta.assistants.create(
    name="Stock market assistant",
    instructions=system_message,
    model=model_name,
)
    thread = create_thread()
    full_info = f"{query} with ticker/symbol {ticker.lower()} \
        with start date {start_date} and end date {end_date}"
    add_message_to_thread(thread.id, full_info)
    queued_run = run_assistant(thread.id, assistant.id)
    run = wait_on_run(queued_run, thread)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return run, messages

def sql_query_generator(query, ticker, start_date, end_date):
    run, raw_response = start_assistant(query, ticker, start_date, end_date)
    messages = as_json(raw_response)
    # Obtain response from the assistant and log it
    interpretation = messages['data'][0]['content'][0]['text']['value']

    return interpretation

def get_data_from_duckdb_with_natural_language_query(nl_query, ticker, start_date, end_date):
    """
    Converts a natural language query into SQL and fetches data from DuckDB.
    """
    # Generate SQL query from natural language query
    sql_query = sql_query_generator(nl_query, ticker, start_date, end_date)
    print(sql_query)
    # Connect to DuckDB and execute the SQL query
    conn = duckdb.connect(db_file)
    data = conn.execute(sql_query).fetchdf()
    conn.close()
    
    return data