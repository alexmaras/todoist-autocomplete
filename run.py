import os
import todoist
import pytz
from string import Template
from datetime import datetime, timedelta
from dotenv import load_dotenv

REQUIRED_ENV_VARIABLES = [
    "TOKEN",
    "AUTOCOMPLETE_LABEL",
    "DAILY_OVERDUE_HOURS_LIMIT",
    "WEEKLY_OVERDUE_HOURS_LIMIT",
    "MONTHLY_OVERDUE_HOURS_LIMIT",
    "LOCAL_TIMEZONE",
]

def main():
    load_dotenv()
    if not all(check_required_env()):
        print("Provide a .env with the following variables:")
        print(REQUIRED_ENV_VARIABLES)
        exit(1)

    print("Connecting to Todoist with provided token...")
    api = todoist.TodoistAPI(os.getenv("TOKEN"))
    api.sync()
    print("Todoist information synced.")

    autocomplete_label_id = find_label(api.state["labels"], os.getenv("AUTOCOMPLETE_LABEL"))
    autocomplete_items = find_autocomplete_items(api.state["items"], autocomplete_label_id)

    overdue_items = find_overdue_items(
            autocomplete_items,
            api.state["labels"],
            os.getenv("DAILY_OVERDUE_HOURS_LIMIT"),
            os.getenv("WEEKLY_OVERDUE_HOURS_LIMIT"),
            os.getenv("MONTHLY_OVERDUE_HOURS_LIMIT"),
            os.getenv("LOCAL_TIMEZONE")
    )

    number_of_items_template = Template("Found $number overdue item${is_plural}")
    print(
        number_of_items_template.substitute(
            number = len(overdue_items),
            is_plural = "" if len(overdue_items) == 1 else "s"
        )
    )

    for item in overdue_items:
        api.items.close(item["id"])

    api.commit()
    print("Items completed")

def check_required_env():
    get_env_vars = lambda required_env: os.getenv(required_env)
    return map(get_env_vars, REQUIRED_ENV_VARIABLES)

def find_label(labels, required_label):
    for label in labels:
        if label["name"] == required_label:
            return label["id"]

def has_label(item, required_label):
    for label in item["labels"]:
        if label == required_label:
            return True
    return False

def find_autocomplete_items(items, label):
    filter_by_label = lambda item: label in item["labels"] and item["checked"] == 0
    autocomplete_items = filter(filter_by_label, items)
    return autocomplete_items

def find_overdue_items(items, labels, overdue_limit_daily, overdue_limit_weekly, overdue_limit_monthly, local_timezone):
    overdue_items = []
    for item in items:
        item_date = item["due"]["date"]
        date = item_date[:-1] if len(item_date) == 20 else item_date
        tz = item["due"]["timezone"] or local_timezone

        now = datetime.now(pytz.timezone(tz))
        due_date = datetime.fromisoformat(date).astimezone(pytz.timezone(tz))

        overdue_limit = overdue_limit_daily
        if has_label(item, find_label(labels, "weekly")):
            overdue_limit_weekly 
        if has_label(item, find_label(labels, "monthly")):
            overdue_limit_monthly 

        overdue_date = due_date + timedelta(hours=int(overdue_limit))
        if now > overdue_date:
            overdue_items.append(item)
    return overdue_items

main()
