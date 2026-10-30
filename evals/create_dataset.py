"""
Create (or update) the strands-agent-golden dataset in Langfuse.

Run from the project root:  python -m evals.create_dataset
Needs LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and LANGFUSE_BASE_URL (loaded from .env).
Items have fixed ids, so re-running updates them instead of creating duplicates.
"""
from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client

DATASET_NAME = "strands-agent-golden"

GITHUB_PROMPT = (
    "Use your http_request tool to fetch "
    "https://api.github.com/repos/strands-agents/sdk-python "
    "and tell me how many stars and open issues it has."
)

ITEMS = [
    {
        "id": "golden-01-greeting",
        "prompt": "Hello! What can you help me with?",
        "expected": (
            "Greets the user and briefly says what it can help with (for example answering "
            "questions, writing, or making HTTP requests) in a few lines, and ends with "
            "'Have a kind day!'"
        ),
        "expects_tool": False,
        "source": "test_agent.py",
    },
    {
        "id": "golden-02-http-capability",
        "prompt": "Can you make HTTP requests?",
        "expected": (
            "Confirms that it can make HTTP requests, in a few lines, without needing to "
            "actually make one, and ends with 'Have a kind day!'"
        ),
        "expects_tool": False,
        "source": "test_agent.py",
    },
    {
        "id": "golden-03-tool-list",
        "prompt": "What tools do you have access to?",
        "expected": (
            "Names http_request as its tool (and does not invent other tools), briefly says "
            "what it does, and ends with 'Have a kind day!'"
        ),
        "expects_tool": False,
        "source": "test_agent.py",
    },
    {
        "id": "golden-04-github-stars",
        "prompt": GITHUB_PROMPT,
        "expected": (
            "States the star count and the open issues count for the repo, notes that the "
            "repo redirects to (was renamed to) strands-agents/harness-sdk, and ends with "
            "'Have a kind day!'"
        ),
        "expects_tool": True,
        "source": "github",
    },
    {
        "id": "golden-05-no-tool",
        "prompt": "What is the capital of France?",
        "expected": (
            "Answers that the capital is Paris, directly and in a line or two, without "
            "calling any tool, and ends with 'Have a kind day!'"
        ),
        "expects_tool": False,
        "source": "no-tool control",
    },
]


def main():
    langfuse = get_client()

    try:
        langfuse.get_dataset(DATASET_NAME)
        print(f"Dataset '{DATASET_NAME}' already exists; updating items.")
    except Exception:
        langfuse.create_dataset(
            name=DATASET_NAME,
            description="Golden prompts for the Strands agent. Expected outputs describe what a correct answer must contain.",
            metadata={"agent": "my_agent.py"},
        )
        print(f"Created dataset '{DATASET_NAME}'.")

    for item in ITEMS:
        langfuse.create_dataset_item(
            id=item["id"],
            dataset_name=DATASET_NAME,
            input={"prompt": item["prompt"]},
            expected_output=item["expected"],
            metadata={"expects_tool": item["expects_tool"], "source": item["source"]},
        )
        print(f"  upserted {item['id']}")

    langfuse.flush()
    print(f"Done: {len(ITEMS)} items.")


if __name__ == "__main__":
    main()
