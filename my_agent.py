import os

from strands import Agent
from strands.vended_tools import http_request
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = (
    "You are a helpful and kind agent. "
    "You give outputs in a few lines. "
    "You always end with 'Have a kind day!'"
)


def build_model():
    # Local dev: MODEL_PROVIDER=ollama. Otherwise None -> Strands' Bedrock default.
    if os.getenv("MODEL_PROVIDER", "").lower() == "ollama":
        from strands.models.ollama import OllamaModel

        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return OllamaModel(host=host, model_id="qwen3.8:27b")
    return None


def setup_tracing():
    # Local dev: Langfuse tracing when LANGFUSE_PUBLIC_KEY is set (needs requirements-dev.txt).
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        from langfuse import get_client

        if not get_client().auth_check():
            print("Langfuse auth check failed; check LANGFUSE_* settings", flush=True)


setup_tracing()

def create_agent():
    return Agent(model=build_model(), system_prompt=SYSTEM_PROMPT, tools=[http_request])


agent = create_agent()


@app.entrypoint
def invoke(payload):
    print("Invoke called with payload:", payload, flush=True)
    prompt = payload.get("prompt", "")
    result = agent(prompt)
    return result.message


if __name__ == "__main__":
    print("Your agent is live ...", flush=True)
    app.run(host="0.0.0.0", port=8080)
