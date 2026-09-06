
@app.route("/add", methods=["POST"])
def add():
    if not session.get("owner"):
        return redirect(url_for("admin"))

    data = load()
    typ = request.form["type"]
from flask import Flask, render_template, request, redirect, url_for, session
from pathlib import Path
import json
import os

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"

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
    return json.loads(DB.read_text(encoding="utf-8"))


def save(data):
    DB.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == "CHANGE_ME":
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


    data[typ].append({
        "name": request.form["name"],
        "details": request.form.get("details", ""),
        "docs": request.form.get("docs", ""),
        "old": request.form.get("old", ""),
        "new": request.form.get("new", "")
    })

    save(data)

    return return redirect(url_for("dashboard"))
