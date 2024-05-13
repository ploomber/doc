from typing import Optional

import chainlit as cl


@cl.header_auth_callback
def header_auth_callback(headers: dict) -> Optional[cl.User]:
    return cl.User(identifier=headers.get("X-Auth-Name", "Anonymous"),
                   metadata={"role": "admin", "provider": "header"})


@cl.on_message
async def on_message(message: cl.Message):
    response = f"Hello, you just sent: {message.content}!"
    await cl.Message(response).send()
