from haystack import Pipeline
from haystack_integrations.components.evaluators import UpTrainEvaluator, UpTrainMetric
from haystack.utils import Secret
from haystack.components.generators.openai import OpenAIGenerator
import wandb
import os
from dotenv import load_dotenv

load_dotenv(".env")
openai_key = os.getenv("OPENAI_API_KEY")

QUESTIONS = [
    "Which is the most popular global sport?",
    "Who created the Python language?",
]
CONTEXTS = [
    [
        "The popularity of sports can be measured in various ways, including TV viewership, \
            social media presence, number of participants, and economic impact. \
            Football is undoubtedly the world's most popular sport with major \
            events like the FIFA World Cup and sports personalities like \
            Ronaldo and Messi, drawing a followership of more than 4 billion people."
    ],
    [
        "Python, created by Guido van Rossum in the late 1980s, is a high-level \
        general-purpose programming language. Its design philosophy emphasizes \
        code readability, and its language constructs aim to help programmers \
        write clear, logical code for both small and large-scale software projects."
    ],
]


pipeline = Pipeline()
evaluator = UpTrainEvaluator(
    metric=UpTrainMetric.FACTUAL_ACCURACY,
    api="openai",
)
pipeline.add_component("evaluator", evaluator)

client = OpenAIGenerator(model="gpt-4")
response1 = client.run("Which is the most popular global sport?")
response2 = client.run("Who created the Python language?")

RESPONSES = [
    response1['replies'][0],
    response2['replies'][0],
]

results = pipeline.run({"evaluator": {"questions": QUESTIONS, "contexts": CONTEXTS, "responses": RESPONSES}})
print(results)