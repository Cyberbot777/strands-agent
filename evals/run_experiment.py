"""
Run the agent on a local Ollama model against every item in the strands-agent-golden
dataset as a Langfuse experiment run. Each item produces a trace linked to the run.

Run from the project root:  python -m evals.run_experiment
Needs Ollama running with the model pulled, plus the LANGFUSE_* variables (loaded from .env).
"""
from langfuse import Evaluation, get_client

from evals.common import (
    DATASET_NAME,
    MODEL_ID,
    check_ends_with_kind_day,
    check_tool_use,
    judge_answer,
    run_agent,
)


def task(*, item, **kwargs):
    return run_agent(item.input["prompt"])


def ends_with_kind_day(*, output, **kwargs):
    ok, _ = check_ends_with_kind_day(output["text"])
    return Evaluation(name="ends_with_kind_day", value=ok, data_type="BOOLEAN")


def tool_use_correct(*, output, metadata, **kwargs):
    ok, detail = check_tool_use((metadata or {}).get("expects_tool"), output["tool_calls"])
    return Evaluation(name="tool_use_correct", value=ok, data_type="BOOLEAN", comment=detail)


def meets_expected_output(*, input, output, expected_output, **kwargs):
    ok, reason = judge_answer(input["prompt"], output["text"], expected_output)
    return Evaluation(name="meets_expected_output", value=ok, data_type="BOOLEAN", comment=reason)


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
