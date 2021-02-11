FROM python:3.8

RUN pip install poetry

COPY pyproject.toml /tmp/install/pyproject.toml
COPY poetry.lock /tmp/install/poetry.lock

RUN poetry config virtualenvs.create false
RUN cd /tmp/install/ && poetry install --no-root

COPY market_clock /app/market_clock

COPY main.py /app/main.py

WORKDIR /app

ENTRYPOINT ["python3"]
