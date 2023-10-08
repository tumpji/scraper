FROM python:3.11-bookworm

# RUN apt-get update -y; apt-get upgrade -y
# RUN pip install --upgrade pip

RUN pip install psycopg2

WORKDIR project

COPY database database
COPY webserver .

CMD python webserver.py
