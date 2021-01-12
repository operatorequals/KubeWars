FROM python:3.7-alpine
WORKDIR /app

COPY bot/main.py bot.py

COPY bot/spacecraft/main.py spacecraft
RUN pip install dashing && \
	chmod +x spacecraft

EXPOSE 7587
CMD ["python", "bot.py"]