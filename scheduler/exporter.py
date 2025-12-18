# scheduler/exporter.py
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_to_csv(schedule, filename="output_schedule.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Service", "Role", "Assigned"])
        for entry in schedule:
            for role, person in entry["assignments"].items():
                writer.writerow([entry["date"], entry["service"], role, person])

def export_to_text(schedule, filename="output_schedule.txt"):
    with open(filename, "w") as f:
        for entry in schedule:
            f.write(f"{entry['date']} - {entry['service']}\n")
            for role, person in entry["assignments"].items():
                f.write(f"  {role}: {person}\n")
            f.write("\n")

def export_to_pdf(schedule, filename="output_schedule.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica", 12)

    for entry in schedule:
        c.drawString(50, y, f"{entry['date']} - {entry['service']}")
        y -= 20
        for role, person in entry["assignments"].items():
            c.drawString(70, y, f"{role}: {person}")
            y -= 15
        y -= 10
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 50
    c.save()