FROM python:3.11-buster


RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 8000

