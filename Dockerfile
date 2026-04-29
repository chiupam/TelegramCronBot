FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo Asia/Shanghai > /etc/timezone

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh \
    && echo '#!/bin/bash' > /app/tglogin \
    && echo 'exec python /app/login.py' >> /app/tglogin \
    && chmod +x /app/tglogin \
    && ln -s /app/tglogin /usr/local/bin/tglogin \
    && mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=DEBUG

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-u", "bot.py"]
