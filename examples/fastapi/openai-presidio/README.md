# OpenAI reverse proxy with Presidio

A simple reverse proxy that intercepts requests and removes PII data.

## Usage (if running on Ploomber Cloud)

```python
from openai import OpenAI

# Initialize client with custom base URL
client = OpenAI(
    # api_key="your-api-key",  # Replace with actual API key
    base_url="https://shrill-sun-9295.ploomberapp.io/v1",  # Custom server URL
)

# Example usage
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Hello, write an email to the customer with email address johndoe@gmail.com",
        },
    ],
)

print(response.choices[0].message.content)

```

## Usage (if running locally)

```python
from openai import OpenAI

# Initialize client with custom base URL
client = OpenAI(
    # api_key="your-api-key",  # Replace with actual API key
    base_url="http://localhost:8080/v1",  # Custom server URL
)

# Example usage
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Hello, write an email to the customer with email address johndoe@gmail.com",
        },
    ],
)

print(response.choices[0].message.content)
```

