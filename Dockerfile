FROM alpine AS builder

WORKDIR /app

RUN wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64; \
    chmod +x cloudflared

################################################################################

FROM python:3.12-slim

ENV TOKEN=''

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
COPY supervisord.conf .

COPY main.py .
COPY requirements.txt .
COPY xserver_captcha.keras .

COPY --from=builder /app/cloudflared /usr/local/bin/cloudflared

RUN apt-get update; \
    apt-get install -y --no-install-recommends supervisor; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    chmod +x /entrypoint.sh; \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/app/supervisord.conf"]
