"""
Shared pieces for the golden-dataset evals: running the agent on Ollama and the three checks.
Used by both run_experiment.py (Langfuse experiment) and test_golden.py (pytest + Allure).
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()

# Must be set before my_agent is imported (it builds its model at import time).
os.environ["MODEL_PROVIDER"] = "ollama"
os.environ.setdefault("BYPASS_TOOL_CONSENT", "true")

import ollama

from my_agent import create_agent

DATASET_NAME = "strands-agent-golden"
MODEL_ID = "qwen3.8:27b"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CLOSING = "Have a kind day!"


def run_agent(prompt):
    """Run a fresh agent (no shared conversation history) on one prompt."""
    agent = create_agent()
    result = agent(prompt)

    tool_calls = [
        block["toolUse"]["name"]
        for message in agent.messages
        for block in message["content"]
        if "toolUse" in block
    ]
    text = "".join(b.get("text", "") for b in result.message["content"]).strip()
    return {"text": text, "tool_calls": tool_calls}


def check_ends_with_kind_day(text):
    ok = text.endswith(CLOSING)
    return ok, f"ends with {CLOSING!r}" if ok else f"does not end with {CLOSING!r}; ends with {text[-40:]!r}"


def check_tool_use(expects_tool, tool_calls):
    ok = bool(expects_tool) == bool(tool_calls)
    return ok, f"expected tool call: {bool(expects_tool)}, tools called: {tool_calls or 'none'}"


def judge_answer(prompt, answer, expected_output):
    """LLM judge: does the answer satisfy the description of a correct answer?"""
    judge_prompt = (
        "You are grading an AI assistant's answer.\n\n"
        f"User prompt: {prompt}\n\n"
        f"Assistant answer:\n{answer}\n\n"
        f"A correct answer must satisfy this description: {expected_output}\n\n"
        'Reply with JSON only: {"pass": true or false, "reason": "<one short sentence>"}. '
        "Pass only if every requirement in the description is met."
    )
    reply = ollama.Client(host=OLLAMA_HOST).chat(
        model=MODEL_ID,
        messages=[{"role": "user", "content": judge_prompt}],
        format="json",
        think=False,
        options={"temperature": 0},
    )
    try:
        verdict = json.loads(reply["message"]["content"])
        return bool(verdict["pass"]), str(verdict.get("reason", ""))
    except (ValueError, KeyError, TypeError):
        return False, f"Judge returned unparseable output: {reply['message']['content'][:200]}"
