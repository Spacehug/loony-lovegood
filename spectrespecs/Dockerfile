FROM python:3.7

ENV TERM xterm
RUN apt-get update && apt-get install -y tzdata build-essential --no-install-recommends && apt-get purge -y --auto-remove

WORKDIR /opt/project/
ADD . .

RUN python -m pip install pip --upgrade && pip install pipenv
RUN pipenv install
