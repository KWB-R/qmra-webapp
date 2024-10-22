# pull official base image
FROM python:3.12.5-slim

# set work directory
WORKDIR qmra

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*
# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt &&\
    pip install --no-cache-dir gunicorn

# copy project
COPY ./qmra ./qmra
COPY ./manage.py .