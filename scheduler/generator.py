# scheduler/generator.py
import csv, calendar, random, yaml

def load_directory(file_path="data/Pioneer Directory.csv"):
    members, roles_map = [], {}
    with open(file_path, newline="") as f:
        rows = list(csv.reader(f))

    header_index = next(i for i, r in enumerate(rows) if "LAST NAME" in r)
    role_index = next(i for i, r in enumerate(rows) if "Roles" in r)

    # Members
    for row in rows[header_index+1:role_index]:
        if len(row) < 7: continue
        last, first, _, _, _, active, role_str = row[:7]
        if active.strip().lower() == "yes":
            roles = role_str.split(",") if role_str else []
            members.append({
                "name": f"{first} {last}",
                "roles": [r.strip() for r in roles if r.strip()]
            })

    # Roles mapping
    for row in rows[role_index+1:]:
        if not row or not row[0].isdigit(): continue
        role_id, service, desc, gender = row[:4]
        roles_map[role_id] = {
            "service": service,
            "description": desc,
            "gender": gender
        }

    return members, roles_map

def get_service_dates(year, month):
    c = calendar.Calendar()
    dates = []
    for day in c.itermonthdates(year, month):
        if day.month == month:
            if day.weekday() == 6:  # Sunday
                dates.append((day, "Sunday AM"))
                dates.append((day, "Sunday PM"))
            elif day.weekday() == 2:  # Wednesday
                dates.append((day, "Wednesday"))
    return dates

def get_week_number(date):
    return ((date.day - 1) // 7) + 1

def generate_schedule(members, roles_map, year, month, settings,
                      last_cleanup="Nancy Reed", last_prep="Kelly Leitner", last_building="Nutley family"):
    absences = settings.get("absences", [])
    preaching = settings["preaching_rotation"]
    fixed = settings["fixed_roles"]
    communion_order = settings["communion_rotation"]
    building_order = settings["building_rotation"]

    dates = get_service_dates(year, month)
    schedule, used = [], {r: [] for r in roles_map.keys()}

    # Rotation indexes
    cleanup_index = (communion_order.index(last_cleanup) + 1) % len(communion_order)
    prep_index = (communion_order.index(last_prep) + 1) % len(communion_order)
    building_index = (building_order.index(last_building) + 1) % len(building_order)

    monthly_cleanup = communion_order[cleanup_index]
    monthly_prep = communion_order[prep_index]
    monthly_building = building_order[building_index]

    # Month parity for PM rotation
    month_parity = (month % 2 == 0)

    for day, service in dates:
        assignments = {}
        week_num = get_week_number(day)

        for role_id, role_info in roles_map.items():
            if service.startswith("Sunday") and "S" not in role_info["service"]:
                continue
            if service.startswith("Wednesday") and "W" not in role_info["service"]:
                continue

            # --- Fixed rules ---
            if role_id == "5":  # Lord's Supper
                if fixed["lord_supper"] not in absences:
                    assignments[role_info["description"]] = fixed["lord_supper"]
                else:
                    eligible = [m for m in members if role_id in m["roles"] and m["name"] not in absences]
                    if eligible:
                        chosen = random.choice(eligible)
                        assignments[role_info["description"]] = chosen["name"]
                continue

            if role_id == "2":  # Teaching
                if fixed["teaching"] not in absences:
                    assignments[role_info["description"]] = fixed["teaching"]
                else:
                    eligible = [m for m in members if role_id in m["roles"] and m["name"] not in absences]
                    if eligible:
                        chosen = random.choice(eligible)
                        assignments[role_info["description"]] = chosen["name"]
                continue

            if role_id == "1":  # Preaching rotation
                if service.startswith("Sunday"):
                    if week_num == 1:
                        assignments[role_info["description"]] = preaching["week1"]
                    elif week_num == 2:
                        assignments[role_info["description"]] = preaching["week2"]
                    elif week_num == 3:
                        assignments[role_info["description"]] = preaching["week3_am"] if service.endswith("AM") else preaching["week3_pm"]
                    elif week_num == 4:
                        if service.endswith("AM"):
                            assignments[role_info["description"]] = preaching["week4_am"]
                        else:
                            assignments[role_info["description"]] = preaching["week4_pm_even_month"] if month_parity else preaching["week4_pm_odd_month"]
                    elif week_num == 5:
                        assignments[role_info["description"]] = preaching["week5_even_month"] if month_parity else preaching["week5_odd_month"]
                continue

            if role_id == "9":  # Communion Prep
                assignments[role_info["description"]] = monthly_prep
                continue

            if role_id == "10":  # Communion Cleanup
                assignments[role_info["description"]] = monthly_cleanup
                continue

            if role_id == "11":  # Building Cleanup
                assignments[role_info["description"]] = monthly_building
                continue

            # --- Fairness rotation for other roles ---
            eligible = [m for m in members if role_id in m["roles"] and m["name"] not in absences]
            already_used = used[role_id]
            available = [m for m in eligible if m["name"] not in already_used]

            if not available:
                used[role_id] = []
                available = eligible

            if available:
                chosen = random.choice(available)
                assignments[role_info["description"]] = chosen["name"]
                used[role_id].append(chosen["name"])

        schedule.append({"date": day, "service": service, "assignments": assignments})
    return schedule

def print_schedule(schedule):
    for entry in schedule:
        print(f"{entry['date']} - {entry['service']}")
        for role, person in entry["assignments"].items():
            print(f"  {role}: {person}")
        print()