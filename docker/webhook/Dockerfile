FROM python:3.7-alpine

WORKDIR /app
EXPOSE 8443

COPY webhook/main.py webhook.py

CMD ["python", "webhook.py"]
