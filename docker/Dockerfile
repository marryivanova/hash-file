FROM repo.saber3d.net/docker/library/python:3.12-bookworm

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3 gunicorn

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
    poetry lock --no-update && \
    poetry install --only=main --no-interaction --no-ansi

COPY . .

RUN mkdir -p store

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV APP_DEBUG=False


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "main:app"]