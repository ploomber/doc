from openai import OpenAI

client = OpenAI()

def get_repo_id(prompt):
    prompt_msg = {
        "role": "system",
        "content": prompt,
    }
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[prompt_msg],
        seed=42,
        stream=False,
    )

    return response.choices[0].message.content
