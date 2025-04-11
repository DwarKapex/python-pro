FROM python:3.12

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app
WORKDIR /app

COPY Makefile pyproject.toml poetry.lock
RUN poetry install --no-root
COPY ./mysite .

ENTRYPOINT [ "python", "/app/mysicte/manage.py", 'runserver' ]
