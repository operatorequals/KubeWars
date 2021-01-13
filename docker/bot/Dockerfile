FROM python:3.7-alpine

WORKDIR /app
EXPOSE 7587

COPY bot/main.py bot.py

RUN pip install dashing

COPY bot/spacecraft/main.py spacecraft

RUN chmod +x spacecraft && \
	ln -s /app/spacecraft /bin/spacecraft
	
# Anti-cheat

#	Remove binaries that establish connections
RUN rm /usr/bin/nc && \
	rm /usr/bin/wget

#	Remove direct shells
RUN rm /bin/sh && \
	rm /bin/ash && \
	rm /bin/busybox

CMD ["python", "bot.py"]
