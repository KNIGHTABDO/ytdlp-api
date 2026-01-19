from flask import Flask, request, send_file, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route("/download", methods=["GET"])
def download():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "missing url"}), 400

    filename = f"{uuid.uuid4()}.mp4"

    try:
        subprocess.run(
            [
                "yt-dlp",
                "-f",
                "mp4",
                "-o",
                filename,
                url
            ],
            check=True
        )
    except subprocess.CalledProcessError:
        return jsonify({"error": "yt-dlp failed"}), 500

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
