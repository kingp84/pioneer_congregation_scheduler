# app.py
import yaml
from flask import Flask, render_template
from scheduler.generator import load_directory, generate_schedule, print_schedule
from scheduler.exporter import export_to_csv, export_to_text, export_to_pdf
from azure_openai import ask_gpt   # <-- import GPT helper

app = Flask(__name__)

def build_schedule(year=2026, month=1):
    with open("config/settings.yaml") as f:
        settings = yaml.safe_load(f)

    members, roles_map = load_directory("data/Pioneer Directory.csv")
    schedule = generate_schedule(members, roles_map, year, month, settings,
                                 last_cleanup="Nancy Reed",
                                 last_prep="Kelly Leitner",
                                 last_building="Nutley family")

    print_schedule(schedule)
    export_to_csv(schedule)
    export_to_text(schedule)
    export_to_pdf(schedule)

    # Ask GPT-4 for a natural language summary
    summary_prompt = f"Summarize this congregation schedule for {month}/{year}:\n{schedule}"
    summary = ask_gpt(summary_prompt, deployment="gpt-4")

    # Print summary to console
    print("\nGPT-4 Summary:\n", summary)

    return schedule, summary

@app.route("/")
def index():
    schedule, summary = build_schedule(2026, 1)
    return render_template("schedule.html", schedule=schedule, summary=summary)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)