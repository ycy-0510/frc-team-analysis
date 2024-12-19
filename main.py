import os
from dotenv import load_dotenv
import requests
import pandas as pd  # 确保导入 pandas 库
from selenium import webdriver
from web import getSchoolAddress

driver = webdriver.Safari()
driver.maximize_window()  # Maximize the browser window

url = "https://raw.githubusercontent.com/franspaco/frc_season_map/refs/heads/master/locations/archive/all_team_locations_2024.json"

response = requests.get(url)
team_locations = response.json()

team_numbers = [
    3008,
    4253,
    5883,
    6245,
    6947,
    6998,
    7130,
    7497,
    7526,
    7589,
    7632,
    7636,
    7645,
    7673,
    7709,
    8020,
    8169,
    8503,
    8569,
    8584,
    8585,
    8595,
    8613,
    8723,
    8725,
    8790,
    8805,
    8806,
    9079,
    9126,
    9427,
    9501,
    9564,
    9715,
    10034,
    10114,
    10390,
]
# team_numbers =[766,812,1538,1572,1622,1972,2102,2485,2543,2658,2710,2827,2839,2984,3128,3255,3341,3647,3704,3749,3965,4160,4276,4419,4738,4919,4984,5025,5137,5474,5514,6072,6515,6695,6885,6995,7419,7441,8020,8119,8870,8888,8891,9084,9452,9573,9730,10336,10392,10586,10625]

load_dotenv()

api_key = os.getenv('API_KEY')

if not api_key:
    raise ValueError("API key not found. Please set the API_KEY environment variable in the .env file.")

headers = {"X-TBA-Auth-Key": api_key}

data = []  # 用于存储所有符合条件的获奖信息

current_year = 2024  # 当前年份
start_year = current_year - 3  # 最近五年的起始年份，包括当前年

for team_number in team_numbers:
    team_key = f"frc{team_number}"
    awards_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/awards"
    root_url = f"https://www.thebluealliance.com/api/v3/team/{team_key}"
    response = requests.get(awards_url, headers=headers)
    response2 = requests.get(root_url, headers=headers)

    print(response2.text)

    # 检查响应状态码
    if response.status_code != 200:
        print(f"Error fetching data for team {team_number}: {response.status_code}")
        print(response.text)
        continue  # 跳过当前队伍，继续下一个

    try:
        awards = response.json()
    except ValueError:
        print(f"Invalid JSON response for team {team_number}")
        continue

    # 确保 awards 是一个列表
    if not isinstance(awards, list):
        print(f"Unexpected response format for team {team_number}")
        print(awards)
        continue
    address = getSchoolAddress(driver,response2.json()['school_name'])
    li = [[], [], []]
    for award in awards:
        year = award["year"]
        if year == 2022:
            li[0].append(award["name"])
        if year == 2023:
            li[1].append(award["name"])
        if year == 2024:
            li[2].append(award["name"])
        # if year >= start_year:
        #     event = award['event_key']
        #     name = award['name']
        #     li.append({
        #         'Team Number': team_number,
        #         'Year': year,
        #         'Award': name,
        #         'Event': event
        #     })
    data.append(
        {
            "Team Number": team_number,
            "name": response2.json()["nickname"],
            "school name": response2.json()["school_name"],
            "website": response2.json()["website"],
            "location": response2.json()["city"] + ", " + response2.json()["state_prov"]+ ", " + response2.json()["country"],
            "address": address,
            "rookie year": response2.json()["rookie_year"],
            "2024": "\n".join(li[2]),
            "2023": "\n".join(li[1]),
            "2022": "\n".join(li[0]),
        }
    )
    print(data[len(data) - 1])


if data:
    # 将数据转换为 DataFrame
    df = pd.DataFrame(data)

    # 按照队伍编号和年份排序
    df = df.sort_values(by=["Team Number"], ascending=[True])

    # 重置索引
    df = df.reset_index(drop=True)
    # 将 DataFrame 保存为 Excel 文件
    df.to_excel("team_awards.xlsx", index=False)
    print("数据已成功保存到 team_awards.xlsx")
else:
    print("No data found.")
