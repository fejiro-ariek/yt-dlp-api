# yt-dlp API — Self-hosted on Render

A lightweight Flask API that wraps `yt-dlp` so you can extract video info and direct download URLs via HTTP requests — perfect for use with n8n, Make, Zapier, or any HTTP client.

---

## Deploy to Render

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/YOUR_USERNAME/yt-dlp-api.git
git push -u origin main
```

### 2. Create a Render Web Service
1. Go to [render.com](https://render.com) and click **New → Web Service**
2. Connect your GitHub repo
3. Set **Environment** to **Docker**
4. Add environment variable:
   - `API_KEY` = `some-secret-key-you-choose`
5. Click **Deploy**

Your service URL will be: `https://your-app-name.onrender.com`

---

## API Endpoints

All endpoints (except `/health`) require the header:
```
X-API-Key: your-secret-key
```

### `GET /health`
Check if the service is running.
```
GET /health
→ { "status": "ok" }
```

---

### `GET /info?url=VIDEO_URL`
Returns metadata about the video.
```
GET /info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ

→ {
    "title": "...",
    "duration": 212,
    "duration_string": "3:32",
    "thumbnail": "https://...",
    "uploader": "Rick Astley",
    "view_count": 1400000000,
    "upload_date": "20091025",
    "formats": [ { "format_id": "...", "ext": "mp4", ... } ]
  }
```

---

### `GET /download-url?url=VIDEO_URL&format=FORMAT`
Returns the direct CDN download URL (no file is downloaded to the server).

- `format` (optional): yt-dlp format string. Default: `bestvideo+bestaudio/best`

```
GET /download-url?url=https://youtu.be/dQw4w9WgXcQ&format=bestaudio

→ { "download_url": "https://rr3---sn-....googlevideo.com/...", "format": "bestaudio" }
```

---

### `GET /audio-url?url=VIDEO_URL`
Shortcut — returns best audio-only direct URL.
```
GET /audio-url?url=https://youtu.be/dQw4w9WgXcQ

→ { "audio_url": "https://..." }
```

---

### `GET /subtitles?url=VIDEO_URL`
Lists available subtitle/caption languages.
```
GET /subtitles?url=https://youtu.be/dQw4w9WgXcQ

→ { "output": "Available subtitles for dQw4w9WgXcQ:\nLanguage  Name\nen        English\n..." }
```

---

## Using in n8n

Add an **HTTP Request** node with these settings:

| Field | Value |
|---|---|
| Method | GET |
| URL | `https://your-app.onrender.com/info` |
| Query Params | `url` = `{{ $json.videoUrl }}` |
| Headers | `X-API-Key` = `your-secret-key` |
| Response Format | JSON |

### Example n8n Workflow
1. **Trigger** (Webhook / Schedule / etc.)
2. **HTTP Request** → `/info` to get video metadata
3. **HTTP Request** → `/audio-url` to get the direct audio link
4. **Do whatever** — send to Telegram, save to Notion, pass to another tool, etc.

---

## Notes

- **Free Render tier**: Instances sleep after 15 min inactivity. First request after sleep takes ~30s. Upgrade to Starter ($7/mo) to keep it always-on.
- **No file storage**: This API only returns URLs and metadata. Files are not downloaded to the server.
- **yt-dlp updates**: YouTube frequently changes their API. The Docker image installs the latest yt-dlp on each build. Redeploy periodically to stay updated.
- **Rate limits**: Render free tier has limited CPU. Don't fire too many concurrent requests.
