FROM python:3.11-buster


# 設定環境變數，指定 Python 輸出為不緩衝模式，並設定時區為 UTC
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Taipei

RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 8000

CMD ["poetry", "run", "uwsgi",  "--socket :8000", "--ini", "Accounting_uwsgi.ini"]