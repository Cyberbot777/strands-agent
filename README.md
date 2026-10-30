# Strands Agent Example

A complete example of building, deploying, and invoking a [Strands](https://www.strands.ai/) AI agent on AWS using [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/).

## What This Is

This repository demonstrates how to create a basic Strands agent with tools, package it in Docker, deploy to AWS Bedrock AgentCore, and invoke it. The example agent is a helpful assistant with HTTP request capabilities.

## Quick Start

### Prerequisites

- Python 3.12+
- AWS Account with CLI configured
- Docker (optional - CodeBuild handles builds)

### Deploy in 3 Steps

```bash
# 1. Install toolkit
pip install bedrock-agentcore-starter-toolkit

# 2. Configure and deploy
agentcore configure -e my_agent.py
agentcore launch

# 3. Test
agentcore invoke '{"prompt": "Hello"}'
```

**For detailed commands, shell-specific examples, and troubleshooting, see [AGENTCORE_CLI_GUIDE.md](./AGENTCORE_CLI_GUIDE.md)**

## Local Testing

Test your agent locally before deploying:

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/Scripts/activate  # Git Bash/Linux
# or
.venv\Scripts\Activate.ps1     # PowerShell

# Install dependencies (requirements-dev.txt adds Ollama support)
uv pip install -r requirements-dev.txt

# Run local tests
python test_agent.py
```

By default the agent uses Amazon Bedrock, so this needs AWS credentials with model access. To run without AWS, use a local Ollama model instead (below).

### Run on a local Ollama model

Set `MODEL_PROVIDER=ollama` to use [Ollama](https://ollama.com/) instead of Bedrock. Pull the model first with `ollama pull qwen3.8:27b`.

```bash
MODEL_PROVIDER=ollama BYPASS_TOOL_CONSENT=true python test_agent.py
```

| Variable | Purpose | Default |
|---|---|---|
| `MODEL_PROVIDER` | Set to `ollama` to use a local Ollama model. Anything else keeps the Bedrock default. | unset (Bedrock) |
| `OLLAMA_HOST` | Ollama server URL (only used when `MODEL_PROVIDER=ollama`) | `http://localhost:11434` |
| `BYPASS_TOOL_CONSENT` | Set to `true` to skip tool confirmation prompts | unset |

To serve the agent over HTTP locally, run `python my_agent.py` and check `curl http://localhost:8080/ping`. Prompts go to `POST /invocations` with a body like `{"prompt": "Hello"}`.

### Run in Docker against local Ollama

The default image is the production image and does not include the `ollama` package. Pass the `INSTALL_DEV` build argument to add it for local use:

```bash
docker build --build-arg INSTALL_DEV=1 -t strands-agent:local-ollama .

docker run --rm -p 8080:8080 \
  -e MODEL_PROVIDER=ollama \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e BYPASS_TOOL_CONSENT=true \
  strands-agent:local-ollama
```

Then, from another terminal:

```bash
curl http://localhost:8080/ping
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Use your http_request tool to fetch https://api.github.com/repos/strands-agents/sdk-python and tell me how many stars it has."}'
```

`host.docker.internal` lets the container reach Ollama on your host (Docker Desktop on Windows and macOS). The container logs a harmless OpenTelemetry export error when no collector is running.

## Project Structure

```
strands-agent/
├── my_agent.py                 # Main agent code (production)
├── test_agent.py               # Local testing script
├── requirements.txt            # Pinned production dependencies
├── requirements-dev.txt        # Adds strands-agents[ollama] for local development
├── Dockerfile                  # Container definition (INSTALL_DEV build arg for Ollama)
├── AGENTCORE_CLI_GUIDE.md      # Detailed CLI reference
└── trust-policy.json           # IAM trust policy
```

## The Agent

A Strands agent with HTTP request capabilities. See [my_agent.py](./my_agent.py) for implementation details.

Key features:
- HTTP request tool for API interactions (`strands.vended_tools.http_request`)
- Amazon Bedrock by default, or a local Ollama model with `MODEL_PROVIDER=ollama`
- Custom system prompt
- AgentCore integration
- OpenTelemetry instrumentation

## Customizing

To customize the agent, edit `my_agent.py`:
- Modify the `SYSTEM_PROMPT` for different behavior
- Add more tools from `strands.vended_tools` (or `strands_tools`)
- Change the Ollama model in `build_model()` (currently `qwen3.8:27b`)
- Adjust the agent configuration

Redeploy with `agentcore launch` after changes.

## Documentation

- **[AGENTCORE_CLI_GUIDE.md](./AGENTCORE_CLI_GUIDE.md)** - Complete CLI reference with all commands, deployment modes, and troubleshooting
- **[my_agent.py](./my_agent.py)** - Agent implementation (production)
- **[test_agent.py](./test_agent.py)** - Local testing script
- **[Dockerfile](./Dockerfile)** - Container configuration

## Additional Resources

- [Strands AI](https://www.strands.ai/) - Agent framework
- [AWS Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/) - Deployment platform
- [AgentCore Starter Toolkit](https://github.com/aws/bedrock-agentcore-starter-toolkit) - Official CLI


