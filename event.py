import requests
from dotenv import load_dotenv
import os

load_dotenv()


def event_type():
    return {
        0: "Regional",
        99: "Offseason",
        3: "Championship Division",
        2: "District Championship",
        4: "Championship Finals",
        1: "District",
        100: "Preseason",
        5: "District Championship Division",
    }


def get_events(year):
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError(
            "API key not found. Please set the API_KEY environment variable in the .env file."
        )

    headers = {"X-TBA-Auth-Key": api_key}
    url = f"https://www.thebluealliance.com/api/v3/events/{year}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_all_events():
    events = []
    for year in range(2022, 2025):
        events.extend(get_events(year))
    eventCodes = []
    for event in events:
        eventCode = event["key"]
        eventCodes.append(eventCode)
    return eventCodes

def get_all_events_name():
    events = []
    for year in range(2022, 2025):
        events.extend(get_events(year))
    eventMap = {}
    for event in events:
        eventMap[event['key']] = event["name"]
    return eventMap

def getAllRegionalAndChampionshipEvents():
    events = []
    for year in range(2022, 2025):
        events.extend(get_events(year))
    eventCodes = []
    for event in events:
        if event["event_type"] in [0, 3, 4]:
            eventCode = event["key"]
            eventCodes.append(eventCode)
    return eventCodes

if __name__ == "__main__":
    print(getAllRegionalAndChampionshipEvents())
    print(get_all_events())
    print(get_all_events_name())
    print(event_type())