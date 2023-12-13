FROM ubuntu:latest

RUN apt update
RUN apt install python3 python3-pip -y

ARG DEBIAN_FRONTEND=noninteractive

RUN pip install fastapi jinja2 uvicorn python-multipart websockets pandas

RUN apt-get clean && apt-get autoremove

COPY /app /app/bbjob

WORKDIR /app/bbjob


# docker build -t bbjob:0.0.1 .
# docker run -p 8000:8000 --gpus all --rm --it bbjob:0.0.1
# uvicorn main:app --reload --host 0.0.0.0