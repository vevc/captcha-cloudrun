#!/usr/bin/env sh

if [ -n "$DOMAIN" ]; then
  sed -i "s/DOMAIN/$DOMAIN/g" /app/backup.sh
  export ENABLE_KEEPALIVE=true
else
  export ENABLE_KEEPALIVE=false
fi

if [ -n "$UUID" ] && [ -n "$TOKEN" ]; then
  export ENABLE_XRAY=true
  export ENABLE_ARGO=true
else
  export ENABLE_XRAY=false
  export ENABLE_ARGO=false
fi

exec "$@"
