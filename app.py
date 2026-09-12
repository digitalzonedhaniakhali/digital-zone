from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pathlib import Path
import json
import os

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"

# Owner password used by both the old /admin login page
# and the new homepage login popup. Change this to something private.
OWNER_PASSWORD = "DZ2026"

DB = Path("data.json")

DEFAULT = {
    "work": [],
    "notice": [],
    "gift": [],
    "discount": []
}


def load():
    if not DB.exists():
        DB.write_text(
            json.dumps(DEFAULT),
            encoding="utf-8"
        )

    return json.loads(
        DB.read_text(encoding="utf-8")
    )


def save(data):
    DB.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


@app.route("/")
def home():
    return render_template("index.html", data=load())


# ------------------------------------------------------------------
# Old server-rendered admin pages (still work, kept as a fallback)
# ------------------------------------------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        if request.form.get("password") == OWNER_PASSWORD:
            session["owner"] = True
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Wrong password"
        )

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if not session.get("owner"):
        return redirect(url_for("admin"))

    return render_template(
        "dashboard.html",
        data=load()
    )


@app.route("/add", methods=["POST"])
def add():

    if not session.get("owner"):
        return redirect(url_for("admin"))

    data = load()
    typ = request.form["type"]

    if typ in data:

        data[typ].append({
            "name": request.form["name"],
            "details": request.form.get("details", ""),
            "docs": request.form.get("docs", ""),
            "old": request.form.get("old", ""),
            "new": request.form.get("new", "")
        })

        save(data)

    return redirect(url_for("dashboard"))


@app.route("/delete/<typ>/<int:i>")
def delete(typ, i):

    if session.get("owner"):

        data = load()

        if typ in data and 0 <= i < len(data[typ]):
            data[typ].pop(i)
            save(data)

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ------------------------------------------------------------------
# New JSON API used by the styled "Owner Dashboard" popup on index.html
# ------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def api_login():

    pw = request.form.get("password", "")

    if pw == OWNER_PASSWORD:
        session["owner"] = True
        return jsonify(ok=True)

    return jsonify(ok=False, error="Wrong password"), 401


@app.route("/api/data")
def api_data():
    return jsonify(load())


@app.route("/api/add", methods=["POST"])
def api_add():

    if not session.get("owner"):
        return jsonify(ok=False, error="Not logged in"), 403

    data = load()
    typ = request.form.get("type", "")
    name = request.form.get("name", "").strip()

    if typ not in data or not name:
        return jsonify(ok=False, error="Invalid input"), 400

    data[typ].append({
        "name": name,
        "details": request.form.get("details", ""),
        "docs": request.form.get("docs", ""),
        "old": request.form.get("old") or 0,
        "new": request.form.get("new") or 0
    })

    save(data)

    return jsonify(ok=True, data=data)


@app.route("/api/delete/<typ>/<int:i>", methods=["POST"])
def api_delete(typ, i):

    if not session.get("owner"):
        return jsonify(ok=False, error="Not logged in"), 403

    data = load()

    if typ in data and 0 <= i < len(data[typ]):
        data[typ].pop(i)
        save(data)

    return jsonify(ok=True, data=data)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
