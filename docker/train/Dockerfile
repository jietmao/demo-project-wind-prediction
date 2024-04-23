FROM python:3.11-slim as base

ENV WORKING_DIR     /app
ENV POETRY_HOME     /opt/poetry
ENV PATH            ${POETRY_HOME}/bin:${PATH}
ENV PYTHONPATH      ${WORKING_DIR}/src
ENV PREFECT_API_URL http://127.0.0.1:4200/api

WORKDIR ${WORKING_DIR}

RUN apt update \
    && apt install -y \
    curl \
    && curl -sSL https://install.python-poetry.org | python -

COPY ./poetry.lock .
COPY ./pyproject.toml .

RUN poetry install --no-root

COPY ./src src
COPY ./config config
COPY ./docker/.aws /root/.aws


FROM base AS test

COPY ./test test
RUN poetry run pytest ./test/test_train.py


FROM base AS app

WORKDIR ${WORKING_DIR}/src
ENTRYPOINT ["poetry", "run", "python", "train.py"]
