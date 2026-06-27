import os
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import database
import generator
import scheduler

load_dotenv()

app = Flask(__name__)
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
TAVILY_KEY = os.environ["TAVILY_API_KEY"]


@app.route("/")
def index():
    return render_template("index.html", issues=database.list_issues())


@app.route("/issue/<int:issue_id>")
def issue(issue_id):
    data = database.get_issue(issue_id)
    if not data:
        return "Issue not found", 404
    reel_map = {p["story_index"]: p for p in data.get("reel_picks", [])}
    return render_template("issue.html", issue=data, reel_map=reel_map)


@app.route("/generate", methods=["POST"])
def generate():
    data = generator.generate_newsletter(ANTHROPIC_KEY, TAVILY_KEY)
    issue_id = database.save(data)
    return redirect(url_for("issue", issue_id=issue_id))


if __name__ == "__main__":
    database.init()
    scheduler.start()
    # use_reloader=False prevents APScheduler from running twice in debug mode
    app.run(debug=True, use_reloader=False)
