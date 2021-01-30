from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    jsonify,
    request,
    flash,
    make_response,
)
import json
import uuid
import os

app = Flask(__name__, static_url_path="")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.secret_key = "thisisasecretkey"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        json_file = open(f"{APP_ROOT}/db/login.json", "r")
        users = json.load(json_file)
        json_file.close()
        for _, value in users.items():
            if value["email"] == email:
                flash("Email already in use!")
                return redirect(url_for("base"))
        uid = str(uuid.uuid4())
        user = {uid: {"uid": uid, "email": email, "password": password}}
        users.update(user)
        json_file = open(f"{APP_ROOT}/db/login.json", "w")
        json_file.seek(0)
        json.dump(users, json_file, indent=2)
        json_file.close()
        os.makedirs(f"{APP_ROOT}/static/users/{email}")
        flash("Account successfully created")
        return redirect(url_for("base"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        json_file = open(f"{APP_ROOT}/db/login.json", "r")
        users = json.load(json_file)
        json_file.close()
        for _, user in users.items():
            if (user["email"] == email) and (user["password"] == password):
                resp = make_response(redirect(url_for("base")))
                resp.set_cookie("tcs", email, max_age=60 * 60 * 24 * 365 * 2)
                flash("Successfully logged in!")
                return resp
        flash("Wrong credentials! Try again.")
        return redirect(url_for("base"))


@app.route("/")
def base():
    loggedIn = False
    userEmail = ""
    if request.cookies.get("tcs"):
        userEmail = request.cookies.get("tcs")
        loggedIn = True
    return render_template("base.html", loggedIn=loggedIn, userEmail=userEmail)


@app.route("/index")
def index():
    userEmail = request.cookies.get("tcs")
    folders = []
    json_file = open(f"{APP_ROOT}/db/data.json", "r")
    datas = json.load(json_file)
    json_file.close()
    for key, value in datas.items():
        if value["email"]==userEmail:
            folders.append(value)
    folders.reverse()
    return render_template("index.html", folders=folders)


@app.route("/addDate", methods=["POST"])
def addDate():
    if request.cookies.get("tcs"):
        userEmail = request.cookies.get("tcs")
        date = request.form.get("date")
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        datas = json.load(json_file)
        json_file.close()
        for key,value in datas.items():
            if value["date"] == date and value["email"]==userEmail:
                folder_id = value["id"]
                # flash("Folder already exists!")
                data_to_return = {
                    "message": "Folder already exists!",
                    "date": date,
                    "id": folder_id
                }
                # return redirect(f"/date/{folder_id}")
                return jsonify(data_to_return)
        id = str(uuid.uuid4())
        newData = {
            id: {
                "id": id,
                "email": userEmail,
                "folder": date,
                "date": date,
                "entries": []
            }
        }
        datas.update(newData)
        os.makedirs(f"{APP_ROOT}/static/users/{userEmail}/{date}")
        ignoreFile = open(f"{APP_ROOT}/static/users/{userEmail}/{date}/.gitignore", "w")
        ignoreFile.write("!.gitignore")
        ignoreFile.close()
        json_file = open(f"{APP_ROOT}/db/data.json", "w")
        json_file.seek(0)
        json.dump(datas, json_file, indent=2)
        json_file.close()
        # flash("Folder created!")
        data_to_return = {
            "message": "Folder created!",
            "date": date,
            "id": id
        }
        # return redirect(f"/date/{id}")
        return jsonify(data_to_return)
    else:
        flash("Login first!")
        return redirect(url_for("base"))


@app.route("/date/<fid>")
def showEntries(fid):
    if request.cookies.get("tcs"):
        userEmail = request.cookies.get("tcs")
        entry_list = []
        entries = []
        folder_name = ""
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        data = json.load(json_file)
        json_file.close()
        for key,value in data.items():
            if value["id"] == fid and value["email"]:
                folder_name = value["folder"]
                entry_list = value["entries"]
        json_file = open(f"{APP_ROOT}/db/entry.json", "r")
        data = json.load(json_file)
        json_file.close()
        for d in data:
            if d["id"] in entry_list:
                entries.append(d)
        # entries.reverse()
        return render_template("entry.html", folder_name=folder_name, entries=entries, fid=fid)
    else:
        flash("Login first!")
        return redirect(url_for("base"))


@app.route("/makeEntry/<fid>", methods=["POST"])
def makeEntry(fid):
    if request.cookies.get("tcs"):
        userEmail = request.cookies.get("tcs")
        folder_id = fid
        id = str(uuid.uuid4())
        title = request.form.get("title")
        lg_name = request.form.get("lg_name")
        link = request.form.get("link")
        meeting_id = request.form.get("meeting_id")
        meeting_password = request.form.get("meeting_password")
        from_time = request.form.get("from_time")
        to_time = request.form.get("to_time")
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        datas = json.load(json_file)
        json_file.close()
        for key,value in datas.items():
            if key==fid:
                value["entries"].append(id)
        json_file = open(f"{APP_ROOT}/db/data.json","w")
        json_file.seek(0)
        json.dump(datas, json_file, indent=2)
        json_file.close()
        json_file = open(f"{APP_ROOT}/db/entry.json", "r")
        entries = json.load(json_file)
        json_file.close()
        data = {
            "id": id,
            "folder_id": folder_id,
            "email": userEmail,
            "title": title,
            "lg_name": lg_name,
            "link": link,
            "meeting_id": meeting_id,
            "meeting_password": meeting_password,
            "from_time": from_time,
            "to_time": to_time
        }
        entries.append(data)
        json_file = open(f"{APP_ROOT}/db/entry.json", "w")
        json_file.seek(0)
        json.dump(entries, json_file, indent=2)
        json_file.close()
        resp = {
            "id": folder_id,
            "message": "Data entry successful!"
        }
        return jsonify(resp)
    else:
        flash("Login first!")
        return redirect(url_for("base"))


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("base")))
    resp.set_cookie("tcs", expires=0)
    return resp


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
