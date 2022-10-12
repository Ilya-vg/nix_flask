FROM python:3.8-slim-buster

WORKDIR ./app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV AM_I_IN_A_DOCKER_CONTAINER True
ENV POSTGRES_PASSWORD 1

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile
COPY . .

CMD ["pipenv", "run", "gunicorn", "main:app", "--workers", "3", "--bind", "0.0.0.0:5000"]
