# syntax=docker/dockerfile:1

FROM python:3.12

WORKDIR /app

COPY . .

RUN pip3 install .

CMD [ "python3", "./bin/run.py"]
