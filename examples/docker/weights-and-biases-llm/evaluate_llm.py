from haystack import Pipeline
from haystack_integrations.components.evaluators import UpTrainEvaluator, UpTrainMetric
from haystack.utils import Secret
from haystack.components.generators.openai import OpenAIGenerator
import wandb
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv(".env")
openai_key = os.getenv("OPENAI_API_KEY")

def evaluate_response(question, context, model_name="gpt-4"):
    # Initialize evaluation pipeline
    pipeline = Pipeline()
    evaluator = UpTrainEvaluator(
        metric=UpTrainMetric.FACTUAL_ACCURACY,
        api="openai",
    )
    pipeline.add_component("evaluator", evaluator)
    
    # Initialize language model generator
    client = OpenAIGenerator(model=model_name)
    response = client.run(question[0])
    
    responses = [response['replies'][0]]
    
    # Run evaluation
    results = pipeline.run({"evaluator": {"questions": question, "contexts": context, "responses": responses}})
    score = results['evaluator']['results'][0][0]['score']
    tokens_used = response['meta'][0]['usage']['total_tokens']
    
    return score, tokens_used, response

def main(args):
    # Initialize W&B
    run = wandb.init(project="llm_monitor", entity="lgutierrwr", config=args)
    
    question =[ "Which is the most popular global sport?"]
    context = [
                [
                    "The popularity of sports can be measured in various ways, including TV viewership, \
                        social media presence, number of participants, and economic impact. \
                        Football (UK) or Soccer (US) is undoubtedly the world's most popular sport with major \
                        events like the FIFA World Cup and sports personalities like \
                        Ronaldo and Messi, drawing a followership of more than 4 billion people."
                ]
            ]
    model_name = wandb.config["model_name"]
    epochs = wandb.config["epochs"]
    
    for epoch in range(1, epochs + 1):
        score, tokens_used, response = evaluate_response(question, context, model_name)
        
        # Log the results
        wandb.log({
            "epoch": epoch,
            "score": score,
            "tokens_used": tokens_used,
            "response": response['replies'][0]
        })
    
    # Finish the W&B run
    wandb.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--model_name", type=str, default="gpt-4", help="Model name for generating responses")
    parser.add_argument("-e", "--epochs", type=int, default=1, help="Number of evaluation epochs")
    
    args = parser.parse_args()
    main(args)