import sys
import subprocess

# ------------------------------------
# Fehlende Python-Pakete automatisch installieren
# ------------------------------------
def ensure_packages():
    packages = ["flask", "pytesseract", "pillow", "requests"]
    for pkg in packages:
        try:
            if pkg == "pillow":
                __import__("PIL")
            else:
                __import__(pkg)
        except ImportError:
            print(f"Installing {pkg} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure_packages()

from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "image_url missing"}), 400

    try:
        r = requests.get(image_url)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")

        ocr_data = pytesseract.image_to_data(
    img,
    lang="deu+eng",
    config="--oem 3 --psm 6",
    output_type=pytesseract.Output.DICT
)


        results = []
        for i in range(len(ocr_data["text"])):
            text = ocr_data["text"][i].strip()
            if text == "":
                continue
            x, y, w, h = (
                ocr_data["left"][i],
                ocr_data["top"][i],
                ocr_data["width"][i],
                ocr_data["height"][i],
            )
            results.append({
                "text": text,
                "x": x,
                "y": y,
                "width": w,
                "height": h
            })

        return jsonify({"text_blocks": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "OCR API running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
