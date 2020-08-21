import os
import todoist
import pytz
from string import Template
from datetime import datetime, timedelta
from dotenv import load_dotenv

REQUIRED_ENV_VARIABLES = [
    "TOKEN",
    "AUTOCOMPLETE_LABEL",
    "OVERDUE_HOURS_LIMIT",
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

    autocomplete_label_id = find_autocomplete_label(api.state["labels"], os.getenv("AUTOCOMPLETE_LABEL"))
    autocomplete_items = find_autocomplete_items(api.state["items"], autocomplete_label_id)
    overdue_items = find_overdue_items(autocomplete_items, os.getenv("OVERDUE_HOURS_LIMIT"), os.getenv("LOCAL_TIMEZONE"))

    number_of_items_template = Template("Found $number overdue item${is_plural}")
    print(
        number_of_items_template.substitute(
            number = len(overdue_items),
            is_plural = "" if len(overdue_items) == 1 else "s"
        )
    )

    for item in overdue_items:
        api.items.complete(item["id"])

    api.commit()
    print("Items completed")

def check_required_env():
    get_env_vars = lambda required_env: os.getenv(required_env)
    return map(get_env_vars, REQUIRED_ENV_VARIABLES)

def find_autocomplete_label(labels, required_label):
    for label in labels:
        if label["name"] == required_label:
            return label["id"]

def find_autocomplete_items(items, label):
    filter_by_label = lambda item: label in item["labels"]
    autocomplete_items = filter(filter_by_label, items)
    return autocomplete_items

def find_overdue_items(items, overdue_limit, local_timezone):
    overdue_items = []
    for item in items:
        item_date = item["due"]["date"]
        date = item_date if len(item_date) == 19 else item_date[:-1]
        tz = item["due"]["timezone"] or local_timezone

        now = datetime.now(pytz.timezone(tz))
        due_date = datetime.fromisoformat(date).astimezone(pytz.timezone(tz))
        overdue_date = due_date + timedelta(hours=int(overdue_limit))
        if now > overdue_date:
            overdue_items.append(item)
    return overdue_items

main()
