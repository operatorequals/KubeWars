FROM python:3.7-alpine
WORKDIR /app
# ADD bot/main.py
COPY bot/main.py bot.py

EXPOSE 7587
CMD ["python", "bot.py"]