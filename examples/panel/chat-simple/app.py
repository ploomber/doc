import requests
import json
import panel as pn

pn.extension(design="material")


url = ""

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
}


# print the response (if you want to see it)


def echo(contents, user, instance):
    data = {
        "messages": [
            {"content": "You are a helpful assistant.", "role": "system"},
            {"content": contents, "role": "user"},
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()["choices"][0]["message"]["content"]


chat_interface = pn.chat.ChatInterface(
    callback=echo,
)

pn.Column(
    "# Echo Bot",
    chat_interface,
).servable()
