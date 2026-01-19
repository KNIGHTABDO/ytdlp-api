import os
import uuid
import subprocess
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

TEMP_DIR = "/tmp"


@app.route("/")
def home():
    return "yt-dlp API is running", 200


@app.route("/download")
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(TEMP_DIR, filename)

    try:
        # Universal yt-dlp command (works for YouTube, TikTok, etc.)
        cmd = [
            "yt-dlp",
            "-f", "bv*+ba/b",              # best video + best audio, fallback safe
            "--merge-output-format", "mp4",
            "--no-playlist",
            "-o", filepath,
            url
        ]

        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        response = send_file(
            filepath,
            mimetype="video/mp4",
            as_attachment=True,
            download_name="video.mp4"
        )

        # Cleanup after response is fully sent
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass

        return response

    except subprocess.CalledProcessError:
        # yt-dlp failed (unsupported, blocked, too long, etc.)
        return jsonify({"error": "Download failed"}), 500

    except Exception:
        # any unexpected error
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
