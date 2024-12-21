FROM python:slim
WORKDIR /app

RUN apt update && apt install -y postgresql-client

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
#ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
ENTRYPOINT ["python", "-u", "app.py"]