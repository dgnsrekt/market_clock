FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
RUN pip install poetry

COPY pyproject.toml /tmp/install/pyproject.toml
COPY poetry.lock /tmp/install/poetry.lock

RUN poetry config virtualenvs.create false
RUN cd /tmp/install/ && poetry install --no-root --no-dev

COPY market_clock /app/market_clock
COPY main.py /app/main.py

EXPOSE 5010
