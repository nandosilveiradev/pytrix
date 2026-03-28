FROM debian:12-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    git \
    tmux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

COPY . .
CMD ["python3", "app.py"]
