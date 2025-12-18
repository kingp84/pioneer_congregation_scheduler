# azure_openai.py
import openai
import os

openai.api_type = "azure"
openai.api_base = "https://pioneercongregation-openai.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt, deployment="gpt-4"):
    response = openai.ChatCompletion.create(
        engine=deployment,
        messages=[
            {"role": "system", "content": "You are a scheduling assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

def validate_fairness(schedule, deployment="gpt-4"):
    # Convert schedule into text
    schedule_text = ""
    for entry in schedule:
        schedule_text += f"{entry['date']} - {entry['service']}\n"
        for role, person in entry["assignments"].items():
            schedule_text += f"  {role}: {person}\n"
        schedule_text += "\n"

    response = openai.ChatCompletion.create(
        engine=deployment,
        messages=[
            {"role": "system", "content": "You are a fairness auditor for congregation schedules."},
            {"role": "user", "content": f"Here is the schedule:\n{schedule_text}\n\nCheck if assignments are fairly distributed among members. Identify repeats, imbalances, or missing roles, and suggest improvements. Assume fairness means members serve about the same number of times, not perfectly equal."}
        ]
    )
    return response["choices"][0]["message"]["content"]
