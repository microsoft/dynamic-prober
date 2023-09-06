# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY src .

EXPOSE 5000

ENTRYPOINT ["gunicorn", "src.main:app"]