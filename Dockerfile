FROM python:3.11-buster


RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 80

ENTRYPOINT ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:80"]