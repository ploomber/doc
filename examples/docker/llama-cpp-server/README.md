# llama-cpp

*Note: You need to add a GPU to your app for this to work.*

Deploy `llama-cpp` server in Ploomber Cloud.


The server is compatible with OpenAI (for chat completion), you can use it as a
drop-in replacement. Once deployed, set the following environment variables.


```sh
export OPENAI_BASE_URL=https://your-app-id.ploomberapp.io/v1
export OPENAI_API_KEY=notakey
```

OpenAI will now make requests to your llama-cpp server:

```python
import openai

client = openai.OpenAI()


messages = [
        {"content": "You are a helpful assistant.", "role": "system"},
        {"content": "Tell me a joke", "role": "user"},
]

response = openai.chat.completions.create(
    model="gpt-3.5-turbo", # this is ignored since we're using our llama-cpp server
    messages=messages,
)

print(response.choices[0].message.content)
```