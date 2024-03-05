import openai
import panel as pn

pn.extension(design="material")

client = openai.OpenAI()


def echo(contents, user, instance):
    data = {
        "messages": [
            {"content": "You are a helpful assistant.", "role": "system"},
            {"content": contents, "role": "user"},
        ]
    }
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo", messages=data["messages"]
    )
    return response.choices[0].message.content


chat_interface = pn.chat.ChatInterface(
    callback=echo,
)

pn.Column(
    "# Simple Panel chat app",
    chat_interface,
).servable()
