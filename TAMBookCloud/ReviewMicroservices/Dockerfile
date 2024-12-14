FROM python:slim
WORKDIR /app

RUN apt update && apt install -y postgresql-client

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

#COPY . .
COPY . /app

ENV PYTHONPATH=/app
EXPOSE 8000
ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]