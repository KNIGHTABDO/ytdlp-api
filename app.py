import os
import uuid
import subprocess
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

TEMP_DIR = "/tmp"


@app.route("/")
def home():
    return "yt-dlp universal API is running", 200


@app.route("/download")
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(TEMP_DIR, filename)

    try:
        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]/best",   # progressive MP4 only (no ffmpeg)
            "--extractor-args", "youtube:player_client=android",
            "--no-playlist",
            "-o", filepath,
            url
        ]

        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        response = send_file(
            filepath,
            mimetype="video/mp4",
            as_attachment=True,
            download_name="video.mp4"
        )

        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass

        return response

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Download failed",
            "details": e.stderr.decode(errors="ignore")[:300]
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
