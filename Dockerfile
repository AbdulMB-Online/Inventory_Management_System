
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV INVENTORY_DB=/data/hardwarestore.db

COPY . .

RUN mkdir -p /data

CMD ["python", "main.py"]
