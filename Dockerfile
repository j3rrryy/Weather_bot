FROM python:3.11.3-slim-bullseye

WORKDIR /app
COPY . .

EXPOSE 8080

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
