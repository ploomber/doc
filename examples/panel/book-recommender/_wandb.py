from wandb.sdk.data_types.trace_tree import Trace
import wandb
import os

class WeightsBiasesTracking:
    def __init__(self) -> None:
        os.environ["WANDB_API_KEY"] = os.getenv("WANDB_API_KEY")
        wandb.init(project=os.getenv("WANDB_PROJECT"), entity=os.getenv("WANDB_ENTITY"))

    def create_trace(self, prompt, response, query, start_time, end_time):
        status = "success"
        status_message = (None,)
        response_text = response.choices[0].message.content
        token_usage = response.usage.total_tokens
        t = self.trace_log(status, status_message, token_usage, start_time, end_time, query, response_text, prompt, "gpt-3.5-turbo")
        t.log(name="openai_trace")
    

    def trace_log(self, status, status_message, token_usage, start_time_ms, end_time_ms, query, response_text, prompt, model_name):
        """
        This function logs a span to Weights and Biases
        """

        root_span = Trace(
                name="root_span",
                kind="tool",  # kind can be "llm", "chain", "agent" or "tool"
                status_code=status,
                status_message=status_message,
                metadata={
                    "token_usage": token_usage,
                    "model_name": model_name,
                },
                start_time_ms=start_time_ms,
                end_time_ms=end_time_ms,
                inputs={"system_prompt": prompt, "query": query},
                outputs={"response": response_text},
            )
        
        return root_span