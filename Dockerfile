# syntax=docker/dockerfile:1.7
# ---------- deps ----------
FROM python:3.12-slim AS deps

WORKDIR /build

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    --prefix=/install \
    -r requirements.txt

# ---------- Common Graphviz Stage ----------
FROM deps AS graphviz-base

COPY --from=deps /install /usr/local

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y graphviz

# ----------- traceplan drawing ----------
FROM graphviz-base AS runtime

COPY --from=deps /install /usr/local

COPY src .

RUN python -m build

RUN mv dist/*.whl /tmp/

RUN pip install /tmp/*.whl

WORKDIR /app

COPY data .