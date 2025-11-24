# AgentCore CLI Quick Reference

> **Speed Tip**: Install [uv](https://astral.sh/uv) for 10-100x faster package management. Then use `uv run agentcore <command>` instead of `agentcore <command>`. Your Dockerfile already uses uv for production builds!

## Prerequisites

### Option A: Traditional Install
```bash
pip install bedrock-agentcore-starter-toolkit
```

### Option B: With UV (Faster)
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
irm https://astral.sh/uv/install.ps1 | iex      # Windows PowerShell

# Then install toolkit
uv pip install bedrock-agentcore-starter-toolkit
```

## 1. Configure New Agent

Set up a new agent with interactive prompts:

```bash
agentcore configure -e <your-agent-file.py>

# With uv (faster)
uv run agentcore configure -e <your-agent-file.py>
```

**Example:**
```bash
agentcore configure -e my_agent.py
```

Creates `.bedrock_agentcore.yaml` with agent configuration.

---

## 2. Deploy Agent

Deploy or update your agent to AWS:

```bash
agentcore launch

# With uv (faster)
uv run agentcore launch
```

**Deployment Modes:**
- `agentcore launch` - CodeBuild (cloud build, recommended)
- `agentcore launch --local` - Local development mode
- `agentcore launch --local-build` - Build locally, deploy to cloud

---

## 3. Invoke Agent

### Option A: AWS Console Sandbox

Navigate to the AgentCore Test Console in AWS and enter JSON payload:
```json
{
  "prompt": "Your question here"
}
```

### Option B: Command Line

**CMD (Command Prompt):**
```cmd
set PYTHONIOENCODING=utf-8 && agentcore invoke "{\"prompt\": \"Hello\"}"
```

**PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"; agentcore invoke '{\"prompt\": \"Hello\"}'
```

**Bash/WSL/Linux:**
```bash
export PYTHONIOENCODING=utf-8
agentcore invoke '{"prompt": "Hello"}'
```

**Complex Payload Example:**
```powershell
$env:PYTHONIOENCODING="utf-8"; agentcore invoke '{\"prompt\": \"What can you help me with?\", \"context\": \"testing\"}'
```

---

## 4. Check Status

View agent deployment status and details:

```bash
agentcore status
```

**With UTF-8 (Windows):**
```powershell
$env:PYTHONIOENCODING="utf-8"; agentcore status
```

Shows:
- Agent ARN and endpoint status
- Region and account info
- CloudWatch log locations
- Dashboard links

---

## 5. View Logs

### Tail Live Logs

```bash
aws logs tail /aws/bedrock-agentcore/runtimes/<AGENT_ARN>-DEFAULT \
  --log-stream-name-prefix "2025/11/22/[runtime-logs]" \
  --follow
```

### View Recent Logs (Last Hour)

```bash
aws logs tail /aws/bedrock-agentcore/runtimes/<AGENT_ARN>-DEFAULT \
  --log-stream-name-prefix "2025/11/22/[runtime-logs]" \
  --since 1h
```

**Example:**
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/my_agent-GfrKzH6wwJ-DEFAULT \
  --log-stream-name-prefix "2025/11/22/[runtime-logs]" \
  --follow
```

---

## 6. Destroy Agent

Remove agent and AWS resources:

```bash
agentcore destroy
```

**Warning:** This deletes the agent runtime, but may preserve ECR repositories and IAM roles.

---

## 7. Get Help

### General Help
```bash
agentcore --help
```

### Command-Specific Help
```bash
agentcore launch --help
agentcore invoke --help
agentcore status --help
agentcore configure --help
agentcore destroy --help
```

---

## UV vs Standard Commands

**Choose your style:**

| Standard (Works Everywhere) | With UV (Faster) |
|-----------------------------|------------------|
| `agentcore configure -e my_agent.py` | `uv run agentcore configure -e my_agent.py` |
| `agentcore launch` | `uv run agentcore launch` |
| `agentcore status` | `uv run agentcore status` |
| `agentcore invoke <payload>` | `uv run agentcore invoke <payload>` |

**When to use UV:**
- Faster execution and dependency resolution
- Consistent with your Dockerfile (already using uv)
- Working without activating virtual environments

**When to use standard:**
- Universal - works for everyone
- Simpler for beginners or documentation
- Inside activated virtual environments

---

## Common Workflows

### First-Time Setup
```bash
# Standard
agentcore configure -e my_agent.py
agentcore launch
agentcore invoke '{"prompt": "Hello"}'

# With UV (faster)
uv run agentcore configure -e my_agent.py
uv run agentcore launch
uv run agentcore invoke '{"prompt": "Hello"}'
```

### Update Existing Agent
```bash
# Make code changes, then deploy
agentcore launch                                    # or: uv run agentcore launch

# Test changes
agentcore status
agentcore invoke '{"prompt": "Test new feature"}'
```

### Debug Issues
```bash
# Check status
agentcore status

# Watch logs in real-time
aws logs tail /aws/bedrock-agentcore/runtimes/<AGENT_ARN>-DEFAULT \
  --log-stream-name-prefix "$(date +%Y/%m/%d)/[runtime-logs]" \
  --follow
```

---

## Key Files

- `.bedrock_agentcore.yaml` - Agent configuration (auto-generated)
- `Dockerfile` - Container definition
- `requirements.txt` - Python dependencies
- `trust-policy.json` - IAM trust policy (if needed)

---

## Environment Variables

**Python Encoding (Windows):**
```cmd
set PYTHONIOENCODING=utf-8
```
```powershell
$env:PYTHONIOENCODING="utf-8"
```

**AWS Credentials:**
Ensure AWS CLI is configured:
```bash
aws configure
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Encoding errors (Windows) | Set `PYTHONIOENCODING=utf-8` |
| Agent not found | Run `agentcore configure` first |
| Deployment fails | Check AWS credentials with `aws sts get-caller-identity` |
| Invoke timeout | Check logs for runtime errors |
| Permission denied | Verify IAM roles in `.bedrock_agentcore.yaml` |

---

## Quick Reference Table

| Command | Purpose |
|---------|---------|
| `agentcore configure -e <file>` | Initialize new agent |
| `agentcore launch` | Deploy/update agent |
| `agentcore invoke <payload>` | Test agent |
| `agentcore status` | Check deployment status |
| `agentcore destroy` | Remove agent |
| `aws logs tail <log-group>` | View runtime logs |

---

## Additional Resources

- **GenAI Observability Dashboard:** Available in AWS Console after deployment
- **CloudWatch Logs:** Found in `agentcore status` output
- **Documentation:** [AWS Bedrock AgentCore Docs](https://docs.aws.amazon.com/bedrock-agentcore/)

