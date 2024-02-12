import os
import wandb
from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.generators.openai import OpenAIGenerator
from haystack_integrations.components.generators.gradient import GradientGenerator
from haystack_integrations.components.generators.cohere import CohereGenerator
from haystack_integrations.components.evaluators import UpTrainEvaluator, UpTrainMetric

load_dotenv(".env")
openai_key = os.getenv("OPENAI_API_KEY")
hf_api_token = os.getenv("HF_API_TOKEN")
gradient_access_token = os.getenv("GRADIENT_ACCESS_TOKEN")
gradient_workspace_id = os.getenv("GRADIENT_WORKSPACE_ID")
cohere_api_key = os.getenv("COHERE_API_KEY")

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Initialize W&B
wandb.init(project="llm_monitor", entity="lgutierrwr")


evaluator = UpTrainEvaluator(
    metric=UpTrainMetric.CRITIQUE_TONE,
    api="openai",
    metric_params={"llm_persona": "informative"}
)

evaluator_pipeline = Pipeline()
evaluator_pipeline.add_component("evaluator", evaluator)

evaluation_results = evaluator_pipeline.run({"evaluator": {"responses": ["The Rhodes Statue was built in 280 BC."]}})

print(evaluation_results)
# client = OpenAIGenerator(model="gpt-4")
# response = client.run("What's Natural Language Processing?")

# generator = GradientGenerator(access_token=gradient_access_token,
#                               workspace_id=gradient_workspace_id,
#                               base_model_slug="llama2-7b-chat",
#                               max_generated_token_count=350)
# generator.warm_up()
# response = generator.run(prompt="What's Natural Language Processing?")

# client = CohereGenerator(api_key=cohere_api_key)
# response = client.run("What's Natural Language Processing?")

# # Loop over OpenAI models
# for model_name in openai_models:
#     response =  client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": prompt}])
#     generated_text = response.choices[0].message.content
#     token_numbers 
#     # Log the prompt and the generated text to W&B
#     wandb.log({"model": model_name, "prompt": prompt, "generated_text": generated_text})
#     print(f"OpenAI {model_name} generated text:", generated_text)

# # Finish the W&B run
# wandb.finish()
