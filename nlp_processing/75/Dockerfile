FROM ghcr.io/astral-sh/uv:0.9.21 AS uv
FROM mcr.microsoft.com/playwright/python:v1.60.0-noble

COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app/75
COPY pyproject.toml uv.lock ./
RUN uv sync --locked
COPY replay.py sandbox.html ./
ENTRYPOINT ["/app/75/.venv/bin/python", "replay.py"]
