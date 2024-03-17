FROM python:3.11-alpine

RUN mkdir '/bot_wildberries'

WORKDIR /bot_wildberries

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .