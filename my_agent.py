from strands import Agent
from strands_tools import http_request
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = (
    "You are a helpful and kind agent. "
    "You give outputs in a few lines. "
    "You always end with 'Have a kind day!'"
)

agent = Agent(system_prompt=SYSTEM_PROMPT, tools=[http_request])


@app.entrypoint
def invoke(payload):
    print("Invoke called with payload:", payload, flush=True)
    prompt = payload.get("prompt", "")
    result = agent(prompt)
    return result.message


if __name__ == "__main__":
    print("Your agent is live ...", flush=True)
    app.run(host="0.0.0.0", port=8080)
