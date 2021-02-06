from flask import (
    Flask, jsonify, url_for, redirect, request
)
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_url_path="")
# app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.secret_key = "thisisasecretkey"
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def home():
    return redirect("/api")

@app.route("/api")
def api():
    return "<h1 align='center'>404 Page Not Found</h1>"

@app.route("/api/auth", methods=["POST"])
def auth():
    email = request.form.get("email")
    password = request.form.get("password")
    if email=="gangpayee@gmail.com" and password=="gangpayee":
        return jsonify({
            "status": "ok",
            "email": email
        })
    else:
        return jsonify({
            "status": "error",
        })

@app.route("/api/upload", methods=["POST"])
def upload():
    details = request.form.get("details")
    codeFile = request.files.get("file")

    if (codeFile):
        fileName = codeFile.filename
        target = f"{APP_ROOT}/static"
        destination = "/".join([target, fileName])
        codeFile.save(destination)

        data = [
            {
                "fileName": fileName,
                "details": details
            }
        ]

        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        prevData = json.load(json_file)
        json_file.close()

        preFileName = prevData[0]["fileName"]

        json_file = open(f"{APP_ROOT}/db/data.json", "w")
        json_file.seek(0)
        json.dump(data, json_file, indent=2)
        json_file.close()

        os.remove(f"{APP_ROOT}/static/{preFileName}")

        return jsonify({
            "status": "ok",
            "message": "uploaded"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "upload failed"
        })

@app.route("/api/get")
def getData():
    json_file = open(f"{APP_ROOT}/db/data.json", "r")
    fileName = json.load(json_file)[0]["fileName"]
    json_file.close()

    f = open(f"{APP_ROOT}/static/{fileName}", "r")
    fileContent = f.read()

    data = {
        "fileName": fileName,
        "content": str(fileContent)
    }

    return jsonify(data)


@app.route("/api/live", methods=["POST"])
def live():
    json_file = open(f"{APP_ROOT}/db/live.json", "r")
    data = json.load(json_file)
    json_file.close()
    text = request.form.get("liveData")
    data = {
        "data": f"{text}"
    }
    json_file = open(f"{APP_ROOT}/db/live.json", "w")
    json_file.seek(0)
    json.dump(data, json_file, indent=2)
    json_file.close()
    return jsonify({"message": "ok"})


@app.route("/api/live/get")
def getLiveData():
    resp = {}
    json_file = open(f"{APP_ROOT}/db/live.json", "r")
    resp = json.load(json_file)
    json_file.close()
    return jsonify(resp)


if __name__=="__main__":
    app.run(port=5001, host='0.0.0.0', debug=True)