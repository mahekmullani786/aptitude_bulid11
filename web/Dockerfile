FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev curl git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY web/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY web /app

# collectstatic could be added for production
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
