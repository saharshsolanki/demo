#!/bin/sh
if [ -z "$PORT"]
then
  PORT=5005
fi
rasa run --model models --enable-api --cors "*" --debug --port $PORT