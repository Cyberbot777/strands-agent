"""
Run the agent on a local Ollama model against every item in the strands-agent-golden
dataset as a Langfuse experiment run. Each item produces a trace linked to the run.

Run from the project root:  python -m evals.run_experiment
Needs Ollama running with the model pulled, plus the LANGFUSE_* variables (loaded from .env).
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()

# Must be set before my_agent is imported (it builds its model at import time).
os.environ["MODEL_PROVIDER"] = "ollama"
os.environ.setdefault("BYPASS_TOOL_CONSENT", "true")

import ollama
from langfuse import Evaluation, get_client

from my_agent import create_agent

DATASET_NAME = "strands-agent-golden"
MODEL_ID = "qwen3.8:27b"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CLOSING = "Have a kind day!"


def task(*, item, **kwargs):
    """Run a fresh agent (no shared conversation history) on one dataset item."""
    agent = create_agent()
    result = agent(item.input["prompt"])

    tool_calls = [
        block["toolUse"]["name"]
        for message in agent.messages
        for block in message["content"]
        if "toolUse" in block
    ]
    text = "".join(b.get("text", "") for b in result.message["content"]).strip()
    return {"text": text, "tool_calls": tool_calls}


def ends_with_kind_day(*, output, **kwargs):
    ok = output["text"].endswith(CLOSING)
    return Evaluation(name="ends_with_kind_day", value=ok, data_type="BOOLEAN")


def tool_use_correct(*, output, metadata, **kwargs):
    expected = bool((metadata or {}).get("expects_tool"))
    used = bool(output["tool_calls"])
    return Evaluation(
        name="tool_use_correct",
        value=expected == used,
        data_type="BOOLEAN",
        comment=f"expected tool call: {expected}, tools called: {output['tool_calls'] or 'none'}",
    )


def meets_expected_output(*, input, output, expected_output, **kwargs):
    """LLM judge: does the answer satisfy the description of a correct answer?"""
    prompt = (
        "You are grading an AI assistant's answer.\n\n"
        f"User prompt: {input['prompt']}\n\n"
        f"Assistant answer:\n{output['text']}\n\n"
        f"A correct answer must satisfy this description: {expected_output}\n\n"
        'Reply with JSON only: {"pass": true or false, "reason": "<one short sentence>"}. '
        "Pass only if every requirement in the description is met."
    )
    reply = ollama.Client(host=OLLAMA_HOST).chat(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        think=False,
        options={"temperature": 0},
    )
    try:
        verdict = json.loads(reply["message"]["content"])
        return Evaluation(
            name="meets_expected_output",
            value=bool(verdict["pass"]),
            data_type="BOOLEAN",
            comment=str(verdict.get("reason", "")),
        )
    except (ValueError, KeyError, TypeError):
        return Evaluation(
            name="meets_expected_output",
            value=False,
            data_type="BOOLEAN",
            comment=f"Judge returned unparseable output: {reply['message']['content'][:200]}",
        )


def pass_rate(*, item_results, **kwargs):
    values = [
        e.value
        for r in item_results
        for e in r.evaluations
        if e.name == "meets_expected_output" and isinstance(e.value, bool)
    ]
    if not values:
        return Evaluation(name="pass_rate", value=0.0, comment="no judged items")
    rate = sum(values) / len(values)
    return Evaluation(name="pass_rate", value=rate, comment=f"{sum(values)}/{len(values)} items passed")


def main():
    langfuse = get_client()
    dataset = langfuse.get_dataset(DATASET_NAME)

    result = dataset.run_experiment(
        name="ollama-qwen3.8-27b",
        description="Strands agent on local Ollama, run against every golden item",
        task=task,
        evaluators=[ends_with_kind_day, tool_use_correct, meets_expected_output],
        run_evaluators=[pass_rate],
        max_concurrency=1,  # one local model; keeps runs independent and readable
        metadata={"provider": "ollama", "model": MODEL_ID},
    )

    print(result.format(include_item_results=True))
    langfuse.flush()


if __name__ == "__main__":
    main()
