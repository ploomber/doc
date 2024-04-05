from openai import AsyncOpenAI
import chainlit as cl
import os

# Enter the personal API key that you set for the host, 
# or leave it blank if you didn't set one
vllm_key = os.environ.get("VLLM_API_KEY") or ""

# Modify this value to match your host, remember to add /v1 at the end
api_base = "https://aged-math-3623.ploomberapp.io/v1"

client = AsyncOpenAI(
    api_key=vllm_key,
    base_url=api_base,
)

# Instrument the OpenAI client
cl.instrument_openai()

settings = {
    "model": "google/gemma-2b-it",
    # ... more settings
}

messages = []

@cl.on_chat_start
def main():
    messages = []
    cl.user_session.set("messages", messages)

@cl.on_message
async def on_message(message: cl.Message):
    messages = cl.user_session.get("messages")
    messages = messages + [
        {
            "content": message.content,
            "role": "user"
        }
    ]
    response = await client.chat.completions.create(
        messages=messages,
        **settings
    )
    messages = messages + [{
        "content": response.choices[0].message.content,
        "role": "assistant",
    }]
    cl.user_session.set("messages", messages)
    await cl.Message(content=response.choices[0].message.content).send()
