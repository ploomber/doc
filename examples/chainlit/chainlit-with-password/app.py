from os import environ

import chainlit as cl


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    username_stored = environ.get("CHAINTLIT_USERNAME")
    password_stored = environ.get("CHAINTLIT_PASSWORD")

    if username_stored is None or password_stored is None:
        raise ValueError(
            "Username or password not set. Please set CHAINTLIT_USERNAME and "
            "CHAINTLIT_PASSWORD environment variables."
        )

    if (username, password) == (username_stored, password_stored):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: str):
    # this is an intermediate step
    await cl.Message(author="Tool 1", content=f"Response from tool1").send()

    # send back the final answer
    await cl.Message(content=f"This is the final answer").send()
