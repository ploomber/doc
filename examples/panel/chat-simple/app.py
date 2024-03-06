from openai import AsyncOpenAI
import panel as pn

pn.extension(design="material")

aclient = AsyncOpenAI()


async def callback(contents, user, instance):
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": contents}],
        stream=True,
    )
    message = ""
    async for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
            yield message


chat_interface = pn.chat.ChatInterface(
    callback=callback,
)

pn.template.FastListTemplate(
    main=[chat_interface],
    sidebar=[],
    busy_indicator=pn.indicators.BooleanStatus(value=False),
    title="Chat with LLaMA (powered by Ploomber Cloud)",
).servable()
