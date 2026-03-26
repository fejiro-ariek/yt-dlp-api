FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg curl nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Install yt-dlp's JS dependency for PO token generation
RUN npm install -g @yt-dlp/yt-dlp-js-runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
