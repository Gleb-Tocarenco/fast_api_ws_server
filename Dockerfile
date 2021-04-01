FROM python:3.8

COPY ./app /app

COPY pyproject.toml pyproject.toml /

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install

CMD ["uvicorn", "app.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
