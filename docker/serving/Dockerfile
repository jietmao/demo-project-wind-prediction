FROM python:3.11-slim as base

ENV WORKDIR         /app
ENV POETRY_HOME     /opt/poetry
ENV PATH            ${POETRY_HOME}/bin:${PATH}
ENV PYTHONPATH      ${WORKDIR}/src

WORKDIR ${WORKDIR}

RUN apt update \
    && apt install -y \
    curl \
    && curl -sSL https://install.python-poetry.org | python -

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install --no-root

COPY ./src src
COPY ./docker/.aws /root/.aws


FROM base AS test

COPY ./test test
RUN poetry run pytest ./test/test_serving.py


FROM base AS app

WORKDIR ${WORKDIR}/src

ENTRYPOINT ["poetry", "run", "uvicorn", "serving:serving"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
