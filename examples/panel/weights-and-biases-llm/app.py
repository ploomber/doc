import panel as pn
from openai import OpenAI
from wandb.sdk.data_types.trace_tree import Trace
from dotenv import load_dotenv
import os
import wandb
import datetime

# load the .env file
load_dotenv(".env")
# Set the WANDB_API_KEY environment variable
os.environ["WANDB_API_KEY"] = os.getenv("WANDB_API_KEY")

# start a wandb run to log to
wandb.init(project="llm-trace-example", entity="lgutierrwr")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def dream_interpreter(query):
    
    model_name = "gpt-3.5-turbo"
    temperature = 0.9
    system_message = "You are a helpful and informative dream interpreter, \
        you draw your knowledge from\
        psychology, culture and symbolism. \
        You receive questions from a user on their dreams and life experiences,\
        and you provide them with insights and guidance. Your tone is empathetic, \
        and has an air of mystery and wisdom. Your responses have a maximum length of 5 sentences"
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query},
    ]
    
    try:
        start_time_ms = datetime.datetime.now().timestamp() * 1000
        response =  client.chat.completions.create(
                model=model_name, 
                messages=messages, 
                temperature=temperature,
                seed=42,
                n=1,
            )
        end_time_ms = round(
                datetime.datetime.now().timestamp() * 1000
            ) 
        
        interpretation = response.choices[0].message.content
        status = "success"
        status_message = (None,)
        response_text = interpretation
        token_usage = response.usage.dict()

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


    except Exception as e:
        end_time_ms = round(
            datetime.datetime.now().timestamp() * 1000
        )  # logged in milliseconds
        status = "error"
        status_message = str(e)
        response_text = ""
        token_usage = {}

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
        
    return interpretation


        



def callback(input_text, user, instance: pn.chat.ChatInterface):
    
    return dream_interpreter(input_text)



chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "Hello, I'm a dream interpreter, a guide to the subconscious \
    realm where dreams reveal our deepest secrets and desires. \
    I explore the symbolic language of dreams to uncover insights \
    about our inner worlds. \
        \n \
    \
    Imagine a journey where your dreams \
    guide you toward self-discovery and insight. \
    Let's navigate this together, using your dreams as a compass \
    to explore the mysteries of your soul. Share your dreams with me, \
    and let's decode the messages hidden within, shedding light on your \
    life's path.\n\
    🪷🧘‍♀️🧿🔥💧🪨🌿🤍🧘🏽‍♀️🌙",
    user="System",
    respond=False,
    avatar="🔮",
)

pn.template.MaterialTemplate(
    title="Dream interpreter",
    main=[chat_interface],
).servable()
