from flask import Flask, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY", "changeme")


def auth(req):
    return req.headers.get("X-API-Key") == API_KEY


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/info", methods=["GET"])
def get_info():
    if not auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url= parameter"}), 400

    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-playlist", url],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        data = json.loads(result.stdout)
        return jsonify(
            {
                "title": data.get("title"),
                "duration": data.get("duration"),
                "duration_string": data.get("duration_string"),
                "thumbnail": data.get("thumbnail"),
                "uploader": data.get("uploader"),
                "uploader_url": data.get("uploader_url"),
                "view_count": data.get("view_count"),
                "like_count": data.get("like_count"),
                "description": data.get("description"),
                "upload_date": data.get("upload_date"),
                "webpage_url": data.get("webpage_url"),
                "extractor": data.get("extractor"),
                "formats": [
                    {
                        "format_id": f.get("format_id"),
                        "format_note": f.get("format_note"),
                        "ext": f.get("ext"),
                        "resolution": f.get("resolution"),
                        "filesize": f.get("filesize"),
                    }
                    for f in data.get("formats", [])
                ],
            }
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Request timed out"}), 504
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse yt-dlp output"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download-url", methods=["GET"])
def get_download_url():
    """Returns the direct CDN/download URL without downloading the file."""
    if not auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    url = request.args.get("url")
    fmt = request.args.get("format", "bestvideo+bestaudio/best")
    if not url:
        return jsonify({"error": "Missing ?url= parameter"}), 400

    try:
        result = subprocess.run(
            ["yt-dlp", "-f", fmt, "--get-url", url],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        urls = result.stdout.strip().split("\n")
        return jsonify(
            {
                "download_url": urls[0] if len(urls) == 1 else urls,
                "format": fmt,
            }
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/audio-url", methods=["GET"])
def get_audio_url():
    """Shortcut to get best audio-only direct URL."""
    if not auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url= parameter"}), 400

    try:
        result = subprocess.run(
            ["yt-dlp", "-f", "bestaudio", "--get-url", url],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        return jsonify({"audio_url": result.stdout.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/subtitles", methods=["GET"])
def get_subtitles():
    """Returns available subtitle/caption languages for a video."""
    if not auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url= parameter"}), 400

    try:
        result = subprocess.run(
            ["yt-dlp", "--list-subs", "--skip-download", url],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return jsonify({"output": result.stdout.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
