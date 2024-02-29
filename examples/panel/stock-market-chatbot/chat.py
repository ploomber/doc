from openai import OpenAI
import os
import pandas as pd


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_image_with_text(image_url, text_query):
    complete_question=f"You are an expert data analyst assistant specializing in reading plots. \
                        You will be presented with a plot that contains stock information. \
                        Please refer to each line using only the label, not the colour. \
                        Provide a high level overview summary that \
                        describes the trends in this plot. \
                        Your answer should be  tailored towards \
                        the user question: {text_query}"
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": complete_question},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content

