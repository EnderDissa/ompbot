FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash bot \
  && mkdir -p /app && chown bot:bot /app

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN chown -R bot:bot /app
RUN chmod +x /app/entrypoint.sh

USER bot
WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
