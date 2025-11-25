FROM python:3.11-alpine

# Cài đặt các dependencies cần thiết cho mysql-connector
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-connector-c-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py students.json .
EXPOSE 8081
CMD ["python","app.py"]
