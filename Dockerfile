FROM alpine AS builder

WORKDIR /app

RUN wget https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip; \
    unzip Xray-linux-64.zip; \
    rm -f Xray-linux-64.zip; \
    mv xray node22; \
    wget -O node20 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64; \
    chmod +x node20; \
    wget -O node18 https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.x86_64; \
    chmod +x node18; \
    wget -O node16 https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64; \
    chmod +x node16

################################################################################

FROM python:3.12-bookworm

ENV UUID='' \
    TOKEN='' \
    DOMAIN=''

WORKDIR /app

COPY app /app
COPY entrypoint.sh /entrypoint.sh

COPY main.py .
COPY requirements.txt .
COPY xserver_captcha.keras .

COPY --from=builder /app/node22 /usr/local/bin/node22
COPY --from=builder /app/node20 /usr/local/bin/node20
COPY --from=builder /app/node18 /usr/local/bin/node18
COPY --from=builder /app/node16 /usr/local/bin/node16

RUN apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates wget vim net-tools supervisor unzip iputils-ping telnet git iproute2; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    chmod +x /entrypoint.sh; \
    chmod +x /app/backup.sh; \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/app/supervisord.conf"]
