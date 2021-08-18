FROM rasa/rasa:latest
ADD . /app/
USER root
RUN chmod -R 777 /app
USER 1001
RUN rasa train
ENTRYPOINT ["/app/server.sh"]