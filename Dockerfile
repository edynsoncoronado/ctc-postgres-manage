FROM postgres:latest

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential\
  python3.9 \
  python3.9-dev \
  python3-pip


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /code/app
WORKDIR /code/app

CMD ["python3", "manage.py"]