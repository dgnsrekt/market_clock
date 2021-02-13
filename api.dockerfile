FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml /tmp/install/pyproject.toml
COPY poetry.lock /tmp/install/poetry.lock

RUN poetry config virtualenvs.create false
RUN cd /tmp/install/ && poetry install --no-root --no-dev

COPY market_clock /app/market_clock
COPY main.py /app/main.py

EXPOSE 5010
