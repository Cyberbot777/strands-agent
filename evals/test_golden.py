"""
One pytest test per item in the strands-agent-golden dataset, reported with Allure.

Run from the project root:  python -m pytest
Then:  allure generate allure-results -o allure-report --clean && allure open allure-report
Needs Ollama running, Langfuse reachable, and the LANGFUSE_* variables (loaded from .env).
"""
import allure
import pytest
from langfuse import get_client

from evals.common import (
    DATASET_NAME,
    check_ends_with_kind_day,
    check_tool_use,
    judge_answer,
    run_agent,
)

TEXT = allure.attachment_type.TEXT
langfuse = get_client()


def load_items():
    items = sorted(langfuse.get_dataset(DATASET_NAME).items, key=lambda i: i.id)
    if not items:
        raise RuntimeError(f"Dataset '{DATASET_NAME}' has no items; run: python -m evals.create_dataset")
    return items


ITEMS = load_items()


@pytest.fixture(scope="session", autouse=True)
def flush_langfuse():
    yield
    langfuse.flush()  # so the trace links in the report resolve


@allure.feature(DATASET_NAME)
@pytest.mark.parametrize("item", ITEMS, ids=[i.id for i in ITEMS])
def test_golden_item(item):
    prompt = item.input["prompt"]
    expected = item.expected_output
    expects_tool = (item.metadata or {}).get("expects_tool")
    allure.dynamic.title(f"{item.id}: {prompt[:60]}")

    with langfuse.start_as_current_observation(
        name="pytest-golden-item",
        as_type="span",
        input=item.input,
        metadata={"dataset_item_id": item.id, "source": "pytest"},
    ) as span:
        allure.dynamic.link(langfuse.get_trace_url(trace_id=span.trace_id), name="Langfuse trace")

        with allure.step("Run agent on Ollama"):
            output = run_agent(prompt)
        span.update(output=output)
        allure.attach(output["text"], name="agent output", attachment_type=TEXT)
        allure.attach(expected, name="expected output", attachment_type=TEXT)

        # (check name, function returning (passed, detail), attachment name for the detail)
        checks = [
            ("ends_with_kind_day", lambda: check_ends_with_kind_day(output["text"]), "ends_with_kind_day detail"),
            ("tool_use_correct", lambda: check_tool_use(expects_tool, output["tool_calls"]), "tool calls"),
            ("meets_expected_output", lambda: judge_answer(prompt, output["text"], expected), "judge reasoning"),
        ]

        failures = []
        for name, check, attachment_name in checks:
            try:
                with allure.step(name):
                    passed, detail = check()
                    allure.attach(detail, name=attachment_name, attachment_type=TEXT)
                    langfuse.create_score(
                        trace_id=span.trace_id,
                        name=name,
                        value=float(passed),
                        data_type="BOOLEAN",
                        comment=detail,
                    )
                    assert passed, detail
            except AssertionError as error:
                failures.append(f"{name}: {error}")  # keep going so all three checks are reported

    assert not failures, "\n".join(failures)
