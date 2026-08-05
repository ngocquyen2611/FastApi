FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry==2.4.1
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-root

COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
