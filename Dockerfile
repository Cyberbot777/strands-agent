FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-2 \
    AWS_DEFAULT_REGION=us-east-2

COPY requirements.txt requirements.txt
RUN uv pip install -r requirements.txt

# Local development only: docker build --build-arg INSTALL_DEV=1 ...
# Adds requirements-dev.txt (Ollama support). Unset by default, so production images exclude it.
ARG INSTALL_DEV=""
COPY requirements-dev.txt requirements-dev.txt
RUN if [ -n "$INSTALL_DEV" ]; then uv pip install -r requirements-dev.txt; fi

# Skipped in the dev image: it pins OpenTelemetry 1.33, which conflicts with the Langfuse SDK.
# Run the dev image with `python -u my_agent.py` instead of the default opentelemetry-instrument CMD.
RUN if [ -z "$INSTALL_DEV" ]; then uv pip install aws-opentelemetry-distro==0.12.2; fi

ENV DOCKER_CONTAINER=1

RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

COPY . .

CMD ["opentelemetry-instrument", "python", "-u", "my_agent.py"]
