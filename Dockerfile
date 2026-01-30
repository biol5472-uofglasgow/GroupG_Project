FROM astral/uv:python3.12-bookworm-slim
WORKDIR /app

COPY pyproject.toml /app/
COPY uv.lock /app/
COPY README.md /app/

ENV UV_NO_DEV=1
RUN uv sync --locked --no-install-project 
COPY src /app/src/


RUN uv sync --locked

ENTRYPOINT ["uv", "run", "gffACAKE"]