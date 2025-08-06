FROM python:3.9-slim-bookworm as base
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y curl && apt-get clean
ENV POETRY_VERSION=1.5.1
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="/opt/poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true

# Setup project
COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev

FROM python:3.9-slim-bookworm
WORKDIR /usr/src/app
COPY --from=base /usr/src/app/.venv /usr/src/app/.venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

COPY socketdock socketdock

ENTRYPOINT ["python",  "-m", "socketdock" ]
