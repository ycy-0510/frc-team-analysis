import os
from dotenv import load_dotenv
import requests
import pandas as pd  # Ensure the pandas library is imported
from selenium import webdriver
import inquirer
import argparse
from colors import bcolors
from web import getSchoolAddress
from event import (
    getAllRegionalAndChampionshipEvents,
    getYearEventsNameAndWeek,
    getAllEvents,
    getAllEventsName,
)
from tqdm import tqdm

# Set up argument parser
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("-d", "--detail", action="store_true", help="Print details")
args = parser.parse_args()


# Function to print details if -d flag is passed
def print_detail(message):
    if args.detail:
        print(message)


print(f"{bcolors.OKBLUE}Welcome to the FRC Team Awards program!{bcolors.ENDC}")
print("This program will fetch and save the awards data for the specified FRC teams.")
print(
    f"{bcolors.WARNING}You can choose whether to set the address for each team or not. Setting the address requires a web browser. It may cause your IP address to be blocked by Google that you will see a reCAPTCHA page when searching if you set the address for too many teams in a short time. {bcolors.ENDC}"
)

questions = [
    inquirer.List(
        "SET_Address",
        message="Do you want to set the address?",
        choices=["No", "Yes"],
    ),
]
answers = inquirer.prompt(questions)
SET_Address = answers["SET_Address"] == "Yes"

event_type_question = [
    inquirer.List(
        "event_type",
        message="Which events would you like to include?",
        choices=["All Events", "Regional and Championship Events"],
    ),
]
event_type_answer = inquirer.prompt(event_type_question)

year_question = [
    inquirer.Text(
        "year",
        message="Enter the year you want to analyze (e.g., 2024)",
        validate=lambda _, x: x.isdigit() and int(x) > 2000,
    ),
]
year_answer = inquirer.prompt(year_question)
analysis_year = int(year_answer["year"])


url = "https://raw.githubusercontent.com/franspaco/frc_season_map/refs/heads/master/locations/archive/all_team_locations_2024.json"

response_award = requests.get(url)
team_locations = response_award.json()


# team_numbers = [
#     3008,
#     4253,
#     5883,
#     6245,
#     6947,
#     6998,
#     7130,
#     7497,
#     7526,
#     7589,
#     7632,
#     7636,
#     7645,
#     7673,
#     7709,
#     8020,
#     8169,
#     8503,
#     8569,
#     8584,
#     8585,
#     8595,
#     8613,
#     8723,
#     8725,
#     8790,
#     8805,
#     8806,
#     9079,
#     9126,
#     9427,
#     9501,
#     9564,
#     9715,
#     10034,
#     10114,
#     10390,
# ]
# team_numbers = [ 766,812,1538,1572,1622,1972,2102,2485,2543,2658,2710,2827,2839,2984,3128,3255,3341,3647,3704,3749,3965,4160,4276,4419,4738,4919,4984,5025,5137,5474,5514,6072,6515,6695,6885,6995,7419,7441,8020,8119,8870,8888,8891,9084,9452,9573,9730,10336,10392,10586,10625,]
load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError(
        "API key not found. Please set the API_KEY environment variable in the .env file."
    )

headers = {"X-TBA-Auth-Key": api_key}

data = []  # Used to store all qualifying award information

print(f"{bcolors.HEADER}Fetching events for the last 3 years...{bcolors.ENDC}")
avalibleEvents = []
if event_type_answer["event_type"] == "All Events":
    avalibleEvents = getAllEvents(analysis_year)
else:
    avalibleEvents = getAllRegionalAndChampionshipEvents(analysis_year)

eventsName = getAllEventsName(analysis_year)
yearEventNameAndWeek = getYearEventsNameAndWeek(analysis_year)

event_selection_question = [
    inquirer.List(
        "selected_events",
        message="Select the event you want to include",
        choices=[
            (yearEventNameAndWeek[event]["name"], event)
            for event in yearEventNameAndWeek
        ],
    ),
]
event_selection_answer = inquirer.prompt(event_selection_question)
selected_events = event_selection_answer["selected_events"]


team_numbers = []
event_teams_url = (
    f"https://www.thebluealliance.com/api/v3/event/{selected_events}/teams"
)
response_event_teams = requests.get(event_teams_url, headers=headers)

if response_event_teams.status_code != 200:
    print(
        f"{bcolors.FAIL}Error fetching teams for event {selected_events}: {response_event_teams.status_code}{bcolors.ENDC}"
    )
    print_detail(response_event_teams.text)
else:
    try:
        event_teams = response_event_teams.json()
        team_numbers = [team["team_number"] for team in event_teams]
    except ValueError:
        print(f"{bcolors.FAIL}Invalid JSON response for event teams{bcolors.ENDC}")
team_numbers = sorted(team_numbers)

driver = None
if SET_Address:
    browser_choices = [
        inquirer.List(
            "browser",
            message="Which browser would you like to use?",
            choices=["Chrome", "Safari", "Firefox"],
        ),
    ]
    browser_answers = inquirer.prompt(browser_choices)
    browser_choice = browser_answers["browser"]
    print(f"{bcolors.HEADER}Opening {browser_choice} browser...{bcolors.ENDC}")
    if browser_choice == "Safari":
        driver = webdriver.Safari()
    elif browser_choice == "Chrome":
        driver = webdriver.Chrome()
    elif browser_choice == "Firefox":
        driver = webdriver.Firefox()
    driver.maximize_window()  # Maximize the browser window

with tqdm(total=len(team_numbers), desc="Fetching team data...", unit="team") as pbar:
    for team_number in team_numbers:
        # print(f"{bcolors.HEADER}Fetching data for team {team_number}...{bcolors.ENDC}")
        pbar.set_description(
            f"{bcolors.HEADER}Fetching data for team {team_number}...{bcolors.ENDC}"
        )
        team_key = f"frc{team_number}"
        awards_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/awards"
        root_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}"
        status_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/events/{analysis_year}/statuses"
        response_award = requests.get(awards_url, headers=headers)
        response_team = requests.get(root_url, headers=headers)
        response_status = requests.get(status_url, headers=headers)
        print_detail(response_team.text)

        # Check response status code
        if response_award.status_code != 200:
            print(
                f"{bcolors.FAIL}Error fetching data for team {team_number}: {response_award.status_code}{bcolors.ENDC}"
            )
            print_detail(response_award.text)
            continue  # Skip the current team and continue to the next one

        try:
            awards = response_award.json()
        except ValueError:
            print(
                f"{bcolors.FAIL}Invalid JSON response for team {team_number}{bcolors.ENDC}"
            )
            continue

        # Ensure awards is a list
        if not isinstance(awards, list):
            print(
                f"{bcolors.FAIL}Unexpected response format for team {team_number}{bcolors.ENDC}"
            )
            print_detail(awards)
            continue
        if SET_Address:
            try:
                address = getSchoolAddress(
                    driver, response_team.json()["school_name"]
                ).replace("Address: ", "")
            except:
                address = "Not available"
        else:
            address = "Not available"
        grades = ["Captain", "1st Pick", "2nd Pick", "Other"]
        li = [[], [], []]
        for award in awards:
            year = award["year"]
            if award["event_key"] not in avalibleEvents:
                continue
            eventName = eventsName[award["event_key"]]
            if analysis_year - year <= 3 and analysis_year - year > 0:
                if len(award["recipient_list"]) > 1:
                    i = 0
                    for teamInfo in award["recipient_list"]:
                        if teamInfo["team_key"] == team_key:
                            li[analysis_year - year - 1].append(
                                f'{eventName}: {award["name"]} ({grades[i]})'
                            )
                        i += 1
                else:
                    li[analysis_year - year - 1].append(f'{eventName}: {award["name"]}')
            print_detail(award)
        year_team_region = []
        eventWeek = yearEventNameAndWeek[selected_events]["week"]
        for event in response_status.json():
            print_detail(eventsName[event])
            try:
                if  yearEventNameAndWeek[event]["week"]< eventWeek:
                    year_team_region.append(eventsName[event])
            except:
                pass
        data.append(
            {
                "Team Number": team_number,
                "name": response_team.json()["nickname"],
                "school name": response_team.json()["school_name"],
                "website": response_team.json()["website"],
                "location": response_team.json()["city"]
                + ", "
                + response_team.json()["state_prov"]
                + ", "
                + response_team.json()["country"],
                "address": address,
                "rookie year": response_team.json()["rookie_year"],
                str(analysis_year - 1): "\n".join(li[0]),
                str(analysis_year - 2): "\n".join(li[1]),
                str(analysis_year - 3): "\n".join(li[2]),
                f"{analysis_year} Events": "\n".join(year_team_region),
            }
        )
        print_detail(data[len(data) - 1])
        pbar.update(1)

if data:
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Sort by team number and year
    df = df.sort_values(by=["Team Number"], ascending=[True])

    # Reset index
    df = df.reset_index(drop=True)
    # Save DataFrame as an Excel file
    if not os.path.exists('output'):
        os.makedirs('output')
    df.to_excel(f"output/team_awards_{analysis_year}_{yearEventNameAndWeek[selected_events]['name']}.xlsx", index=False)

    print(
        f"{bcolors.OKGREEN}Data has been successfully saved to output/team_awards_{analysis_year}_{yearEventNameAndWeek[selected_events]['name']}.xlsx{bcolors.ENDC}"
    )
else:
    print(f"{bcolors.FAIL}No data found.{bcolors.ENDC}")
