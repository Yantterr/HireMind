FROM python:3.13


COPY requirements.txt .

RUN pip install -r requirements.txt

ENV REDIS_HOST="127.0.0.1"
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=""

ENV HOST="localhost"
ENV PORT=8000

ENV JWT_SECRET_KEY="435378289u3tiojezu8jiosfdjue8jio"
ENV JWT_EXPIRE_MINUTES=3600
ENV JWT_ALGORITHM="HS256"


ARG GPT_API_KEY
ENV GPT_API_KEY=${GPT_API_KEY}

ENV BACKEND_CORS_ORIGINS="http://localhost"

RUN apt-get update && apt-get install -y redis-server

CMD redis-server --daemonize yes && python -m src.main