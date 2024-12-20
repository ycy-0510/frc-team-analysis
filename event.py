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


def getAllEvents(analysis_year):
    events = []
    for year in range(analysis_year - 3, analysis_year):
        events.extend(get_events(year))
    eventCodes = []
    for event in events:
        eventCode = event["key"]
        eventCodes.append(eventCode)
    return eventCodes


def getYearEventsNameAndWeek(analysis_year):
    events = get_events(analysis_year)
    eventMap = {}
    for event in events:
        eventMap[event["key"]] = {"name": event["name"], "week": event["week"]}
    return eventMap


def getAllEventsName(analysis_year):
    events = []
    for year in range(analysis_year - 3, analysis_year + 1):
        events.extend(get_events(year))
    eventMap = {}
    for event in events:
        eventMap[event["key"]] = event["name"]
    return eventMap


def getAllRegionalAndChampionshipEvents(analysis_year):
    events = []
    for year in range(analysis_year - 3, analysis_year):
        events.extend(get_events(year))
    eventCodes = []
    for event in events:
        if event["event_type"] in [0, 3, 4]:
            eventCode = event["key"]
            eventCodes.append(eventCode)
    return eventCodes


if __name__ == "__main__":
    print(getAllRegionalAndChampionshipEvents(2025))
    print(getAllEvents(2025))
    print(getAllEventsName(2025))
    print(getYearEventsNameAndWeek(2025))
    print(event_type())
