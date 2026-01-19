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
        # yt-dlp command (TikTok no watermark)
        cmd = [
            "yt-dlp",
            "-f", "mp4",
            "-o", filepath,
            "--no-playlist",
            "--merge-output-format", "mp4",
            url
        ]

        subprocess.run(cmd, check=True)

        response = send_file(
            filepath,
            mimetype="video/mp4",
            as_attachment=True,
            download_name="video.mp4"
        )

        # delete file AFTER response is sent
        @response.call_on_close
        def cleanup():
            try:
                os.remove(filepath)
            except:
                pass

        return response

    except subprocess.CalledProcessError:
        return jsonify({"error": "Download failed"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
