FROM python:3.11-bookworm

# RUN apt-get update -y; apt-get upgrade -y
# RUN pip install --upgrade pip

RUN pip install scrapy scrapy-playwright psycopg2
RUN playwright install --with-deps firefox

WORKDIR project

COPY database database
COPY scraper .

# run command:
CMD scrapy crawl sreality

