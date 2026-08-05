FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry==1.8.3
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry lock --no-update
RUN poetry install --no-interaction --no-root

COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]