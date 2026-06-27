import os
from flask import Flask, render_template, jsonify, abort
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_latest, get_all, get_by_id
from scheduler import start_scheduler
from generator import generate_newsletter, week_label
from database import save_newsletter

app = Flask(__name__)


@app.route("/")
def index():
    newsletter = get_latest()
    all_issues = get_all()
    return render_template("index.html", newsletter=newsletter, all_issues=all_issues)


@app.route("/issue/<int:newsletter_id>")
def issue(newsletter_id):
    newsletter = get_by_id(newsletter_id)
    if not newsletter:
        abort(404)
    all_issues = get_all()
    return render_template("index.html", newsletter=newsletter, all_issues=all_issues)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Manual trigger endpoint for testing."""
    try:
        parsed, raw = generate_newsletter()
        label = week_label()
        save_newsletter(
            week_label=label,
            stories=parsed["stories"],
            top_picks=parsed["top_picks"],
            raw_response=raw,
        )
        return jsonify({"status": "ok", "week_label": label})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/issues")
def api_issues():
    return jsonify(get_all())


if __name__ == "__main__":
    init_db()
    scheduler = start_scheduler()
    try:
        app.run(debug=False, port=5000, use_reloader=False)
    finally:
        scheduler.shutdown()
