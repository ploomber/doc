import openai
from openai import OpenAI
import datetime
from wandb.sdk.data_types.trace_tree import Trace
from dotenv import load_dotenv
import os
import wandb

# start a wandb run to log to
wandb.init(project="llm-trace-example", entity="lgutierrwr")

# load the .env file
load_dotenv(".env")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# define your conifg
model_name = "gpt-3.5-turbo"
temperature = 0.7
system_message = "You are a helpful assistant that always replies in 3 concise bullet points using markdown."

queries_ls = [
    "What is the capital of France?",
    "How do I boil an egg?" * 10000,  # deliberately trigger an openai error
    "What to do if the aliens arrive?",
]

for query in queries_ls:
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query},
    ]

    start_time_ms = datetime.datetime.now().timestamp() * 1000
    try:
        response =  client.chat.completions.create(
            model=model_name, messages=messages, temperature=temperature
        )

        end_time_ms = round(
            datetime.datetime.now().timestamp() * 1000
        )  # logged in milliseconds
        status = "success"
        status_message = (None,)
        response_text = response.choices[0].message.content
        token_usage = response.usage.dict()

    except Exception as e:
        end_time_ms = round(
            datetime.datetime.now().timestamp() * 1000
        )  # logged in milliseconds
        status = "error"
        status_message = str(e)
        response_text = ""
        token_usage = {}

    # create a span in wandb
    root_span = Trace(
        name="root_span",
        kind="llm",  # kind can be "llm", "chain", "agent" or "tool"
        status_code=status,
        status_message=status_message,
        metadata={
            "temperature": temperature,
            "token_usage": token_usage,
            "model_name": model_name,
        },
        start_time_ms=start_time_ms,
        end_time_ms=end_time_ms,
        inputs={"system_prompt": system_message, "query": query},
        outputs={"response": response_text},
    )

    # log the span to wandb
    root_span.log(name="openai_trace")