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

# Install dependencies
uv pip install -r requirements.txt

# Run local tests
python test_agent.py
```

This tests the agent logic without deploying to AWS.

## Project Structure

```
strands-agent/
├── my_agent.py                 # Main agent code (production)
├── test_agent.py               # Local testing script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── AGENTCORE_CLI_GUIDE.md      # Detailed CLI reference
└── trust-policy.json           # IAM trust policy
```

## The Agent

A Strands agent with HTTP request capabilities. See [my_agent.py](./my_agent.py) for implementation details.

Key features:
- HTTP request tool for API interactions
- Custom system prompt
- AgentCore integration
- OpenTelemetry instrumentation

## Customizing

To customize the agent, edit `my_agent.py`:
- Modify the `SYSTEM_PROMPT` for different behavior
- Add more tools from `strands_tools`
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


