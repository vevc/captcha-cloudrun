#!/bin/bash

# sleep random 0~600 seconds
sleep $((RANDOM % 601))

status=$(curl -o /dev/null -s -w "%{http_code}" https://DOMAIN)
echo `date "+%Y-%m-%d %H:%M:%S"` - Request: https://DOMAIN, Response: $status > /tmp/backup.log
