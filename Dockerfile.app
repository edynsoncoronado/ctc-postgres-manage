FROM python:3.9-slim-buster

RUN apt-get update && apt-get install --no-install-recommends -y \
  openssh-server \
  sshpass \
  && /etc/init.d/ssh start

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./app /home/app
RUN pip3 install --no-cache-dir --upgrade -r /home/app/requirements.txt

WORKDIR /home/app