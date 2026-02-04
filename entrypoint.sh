#!/usr/bin/env sh

if [ -n "$TOKEN" ]; then
  export ENABLE_ARGO=true
else
  export ENABLE_ARGO=false
fi

exec "$@"
