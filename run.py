import os
import todoist
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Connecting to Todoist with provided token...")
    api = todoist.TodoistAPI(os.getenv("TOKEN"))
    api.sync()
    print("Todoist information synced.")

    autocomplete_label_id = find_autocomplete_label(api.state["labels"], os.getenv("AUTOCOMPLETE_LABEL"))

    autocomplete_items = find_autocomplete_items(api.state["items"], autocomplete_label_id)

def find_autocomplete_label(labels, required_label):
    for label in labels:
        if label["name"] == required_label:
            return label["id"]

def find_autocomplete_items(items, label):
    autocomplete_items = []

    for item in items:
        print(item)
        print("------")

main()
