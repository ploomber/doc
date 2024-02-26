import chainlit as cl


@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: str):
    # this is an intermediate step
    await cl.Message(author="Tool 1", content=f"Response from tool1", indent=1).send()

    # send back the final answer
    await cl.Message(content=f"This is the final answer").send()