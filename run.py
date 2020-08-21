import os
import todoist
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

main()
