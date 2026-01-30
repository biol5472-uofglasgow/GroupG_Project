FROM astral/uv:python3.12-bookworm-slim



COPY pyproject.toml /app
COPY src /app

WORKDIR /app
RUN uv run gffACAKE