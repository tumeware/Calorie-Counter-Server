FROM ubuntu:18.04

ARG TOKEN_KEY
ARG STRIPE_KEY
ARG MAIL_PASSWORD
ARG MAIL_USERNAME
ARG MAIL_DEFAULT_SENDER
ARG MONGODB_URI
ARG STRIPE_WEBHOOKS_SECRET

ENV TOKEN_KEY ${TOKEN_KEY}
ENV STRIPE_KEY ${STRIPE_KEY}
ENV MAIL_PASSWORD ${MAIL_PASSWORD}
ENV MAIL_USERNAME ${MAIL_USERNAME}
ENV MAIL_DEFAULT_SENDER ${MAIL_DEFAULT_SENDER}
ENV MONGODB_URI ${MONGODB_URI}
ENV STRIPE_WEBHOOKS_SECRET ${STRIPE_WEBHOOKS_SECRET}

LABEL maintainer="Tume Neuvonen <tumeware@gmail.com>"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# Copy server files and requirements file
COPY ./requirements.txt /app/requirements.txt
COPY ./start.py /app/start.py

RUN mkdir app/misc && mkdir app/routes

COPY misc/* /app/misc/
COPY routes/* /app/routes/

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "gunicorn", "-b", "0.0.0.0:80", "start:app" ]

## how to build and run on local:
# docker build -t magicpill-server:[TAG] .
# docker container run -it -d -p 80:8080 magicpill-server:[TAG]
# => localhost
