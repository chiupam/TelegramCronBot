#!/bin/bash
set -e

if [ "$1" = "tglogin" ]; then
    exec /app/tglogin
fi

exec "$@"
