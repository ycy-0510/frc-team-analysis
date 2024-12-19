import os
from dotenv import load_dotenv
import requests
import pandas as pd  # Ensure the pandas library is imported
from selenium import webdriver
from web import getSchoolAddress
from event import getAllRegionalAndChampionshipEvents
from event import getAllEvents
from event import getAllEventsName
import inquirer
from colors import bcolors

print(f"{bcolors.OKBLUE}Welcome to the FRC Team Awards program!{bcolors.ENDC}")
print("This program will fetch and save the awards data for the specified FRC teams.")
print(f"{bcolors.WARNING}You can choose whether to set the address for each team or not. Setting the address requires a web browser. It may cause your IP address to be blocked by Google that you will see a reCAPTCHA page when searching if you set the address for too many teams in a short time. {bcolors.ENDC}")

questions = [
    inquirer.List(
        "SET_Address",
        message="Do you want to set the address?",
        choices=["No","Yes"],
    ),
]
answers = inquirer.prompt(questions)
SET_Address = (answers['SET_Address']== 'Yes')

driver = None
if SET_Address:
    browser_choices = [
        inquirer.List(
            "browser",
            message="Which browser would you like to use?",
            choices=["Safari", "Chrome", "Firefox"],
        ),
    ]
    browser_answers = inquirer.prompt(browser_choices)
    browser_choice = browser_answers["browser"]

    if browser_choice == "Safari":
        driver = webdriver.Safari()
    elif browser_choice == "Chrome":
        driver = webdriver.Chrome()
    elif browser_choice == "Firefox":
        driver = webdriver.Firefox()
    driver.maximize_window()  # Maximize the browser window

url = "https://raw.githubusercontent.com/franspaco/frc_season_map/refs/heads/master/locations/archive/all_team_locations_2024.json"

response = requests.get(url)
team_locations = response.json()

# team_numbers = [3008,4253,5883,6245,6947,6998,7130,7497,7526,7589,7632,7636,7645,7673,7709,8020,8169,8503,8569,8584,8585,8595,8613,8723,8725,8790,8805,8806,9079,9126,9427,9501,9564,9715,10034,10114,10390]
team_numbers =[766,812,1538,1572,1622,1972,2102,2485,2543,2658,2710,2827,2839,2984,3128,3255,3341,3647,3704,3749,3965,4160,4276,4419,4738,4919,4984,5025,5137,5474,5514,6072,6515,6695,6885,6995,7419,7441,8020,8119,8870,8888,8891,9084,9452,9573,9730,10336,10392,10586,10625]

load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError(
        "API key not found. Please set the API_KEY environment variable in the .env file."
    )

headers = {"X-TBA-Auth-Key": api_key}

data = []  # Used to store all qualifying award information

current_year = 2024  # Current year
start_year = (
    current_year - 3
)  # Start year of the last five years, including the current year

avalibleEvents = getAllRegionalAndChampionshipEvents()
event_type_question = [
    inquirer.List(
        "event_type",
        message="Which events would you like to include?",
        choices=["All Events", "Regional and Championship Events"],
    ),
]
event_type_answer = inquirer.prompt(event_type_question)
if event_type_answer["event_type"] == "All Events":
    avalibleEvents = getAllEvents()
else:
    avalibleEvents = getAllRegionalAndChampionshipEvents()

eventsName = getAllEventsName()

for team_number in team_numbers:
    print(f"{bcolors.HEADER}Fetching data for team {team_number}...{bcolors.ENDC}")
    team_key = f"frc{team_number}"
    awards_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/awards"
    root_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}"
    response = requests.get(awards_url, headers=headers)
    response2 = requests.get(root_url, headers=headers)
    print(response2.text)

    # Check response status code
    if response.status_code != 200:
        print(f"{bcolors.FAIL}Error fetching data for team {team_number}: {response.status_code}{bcolors.ENDC}")
        print(response.text)
        continue  # Skip the current team and continue to the next one

    try:
        awards = response.json()
    except ValueError:
        print(f"{bcolors.FAIL}Invalid JSON response for team {team_number}{bcolors.ENDC}")
        continue

    # Ensure awards is a list
    if not isinstance(awards, list):
        print(f"{bcolors.FAIL}Unexpected response format for team {team_number}{bcolors.ENDC}")
        print(awards)
        continue
    if SET_Address:
        address =  getSchoolAddress(driver, response2.json()['school_name']).replace("Address: ", "")
    else:
        address = "Not available"
    grades = ["Captain", "1st Pick", "2nd Pick", "Other"]
    li = [[], [], []]
    for award in awards:
        year = award["year"]
        if award["event_key"] not in avalibleEvents:
            continue
        eventName = eventsName[award["event_key"]]
        if year == 2022:
            if len(award["recipient_list"]) > 1:
                i = 0
                for teamInfo in award["recipient_list"]:
                    if teamInfo["team_key"] == team_key:
                        li[0].append(f'{grades[i]}: {award["name"]}({eventName})')
                    i += 1
            else:
                li[0].append(f'{award["name"]}({eventName})')
        if year == 2023:
            if len(award["recipient_list"]) > 1:
                i = 0
                for teamInfo in award["recipient_list"]:
                    if teamInfo["team_key"] == team_key:
                        li[1].append(f'{grades[i]}: {award["name"]}({eventName})')
                    i += 1
            else:
                li[1].append(f'{award["name"]}({eventName})')
        if year == 2024:
            if len(award["recipient_list"]) > 1:
                i = 0
                for teamInfo in award["recipient_list"]:
                    if teamInfo["team_key"] == team_key:
                        li[2].append(f'{grades[i]}: {award["name"]}({eventName})')
                    i += 1
            else:
                li[2].append(f'{award["name"]}({eventName})')
        print(award)
    data.append(
        {
            "Team Number": team_number,
            "name": response2.json()["nickname"],
            "school name": response2.json()["school_name"],
            "website": response2.json()["website"],
            "location": response2.json()["city"]
            + ", "
            + response2.json()["state_prov"]
            + ", "
            + response2.json()["country"],
            "address": address,
            "rookie year": response2.json()["rookie_year"],
            "2024": "\n".join(li[2]),
            "2023": "\n".join(li[1]),
            "2022": "\n".join(li[0]),
        }
    )
    print(data[len(data) - 1])


if data:
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Sort by team number and year
    df = df.sort_values(by=["Team Number"], ascending=[True])

    # Reset index
    df = df.reset_index(drop=True)
    # Save DataFrame as an Excel file
    df.to_excel("team_awards.xlsx", index=False)
    print(f"{bcolors.OKGREEN}Data has been successfully saved to team_awards.xlsx{bcolors.ENDC}")
else:
    print(f"{bcolors.FAIL}No data found.{bcolors.ENDC}")
