FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh && \
    ln -sf /app/entrypoint.sh /usr/local/bin/tglogin

ENV PYTHONUNBUFFERED=1
ENV SESSION_PATH=/app/data/bot.session
ENV CONFIG_DIR=/app/data

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-u", "bot.py"]
