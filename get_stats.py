#!/usr/bin/env python3

import requests
import re
import numpy as np
import time
import pandas as pd

team_labels = ["ATL", "CHI", "CON", "DAL", "IND", "LAS", "LVA", "MIN", "NYL", "PHO", "SEA", "WAS"]
years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]


# %%
stats = np.zeros((23))
team_list = []

for year in years:
    for t in range(0, len(team_labels)):
        print(year, team_labels[t])
        time.sleep(2)
        url = "https://www.basketball-reference.com/wnba/teams/" + team_labels[t] + "/" + year + ".html"
        try:
            response = requests.get(url, proxies={'http': None, 'https': None})
            if response.status_code == 200: #success
                html_content = response.text
                
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
                #if response.status_code == '429':
                retry_after = response.headers.get("Retry-After")
                print(f"Retry after {retry_after} seconds")
                response = requests.get(url, proxies={'http': None, 'https': None})
                html_content = response.text

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")


        ind1 = html_content.find("Team/G")
        ind2 = html_content.find("</tr>", ind1, len(html_content))

        team_stats = html_content[ind1:ind2]

        column_names = []
        values = []
        for i in re.finditer("data-stat=\"", team_stats):
            temp = team_stats[i.end():team_stats.find("</td>", i.end(), len(team_stats))]
            if temp.split("\" >")[1] != "":
                column_names.append(temp.split("\" >")[0])
                
                values.append(temp.split("\" >")[1])
        team_list.append(team_labels[t])
        team_year = np.asarray(values).astype(float)
        team_year = np.append(team_year, float(year))
        column_names.append("year")
        stats = np.vstack([stats, team_year])

        
teams = pd.DataFrame(data=stats[1:],
                  columns=column_names)

teams['team'] = team_list
teams.to_csv('/home/pi/wnba_predictions/team_stats.csv')

# %%


# %%
team_a_list = []
team_b_list = []
team_a_pts_list = []
team_b_pts_list = []
year_list = []
date_list = []

for year in years:
    print(year)
    time.sleep(5)
    url = "https://www.basketball-reference.com/wnba/years/"+ year + "_games.html"
    try:
        response = requests.get(url, proxies={'http': None, 'https': None})
        if response.status_code == 200: #success
            html_content = response.text
                    
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            if response.status_code == '429':
                time.sleep(3605)
            response = requests.get(url, proxies={'http': None, 'https': None})
            html_content = response.text

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    ind1 = html_content.find("<tbody>")
    ind2 = html_content.find("</table>")

    html_content = html_content[ind1:ind2]

    games = html_content.split("\n")
    

    for game in games:
        if game.find("Playoffs")>0 or len(game) < 1:
            continue
        team_a = game[game.find("visitor_team_name")+24:game.find("visitor_team_name")+27]
        team_a_pts = game[game.find("visitor_pts") + 14: game.find("visitor_pts") + 17]
        if team_a_pts[2] == '<':
            team_a_pts = team_a_pts[0:2]
        elif team_a_pts[2] == '/':
            team_a_pts = team_a_pts[0]
        elif team_a_pts[0] == '<':
            team_a_pts = 0
        team_a_pts = float(team_a_pts)

        team_b = game[game.find("home_team_name")+21:game.find("home_team_name")+24]
        team_b_pts = game[game.find("home_pts") + 11: game.find("home_pts") + 14]
        if team_b_pts[2] == '<':
            team_b_pts = team_b_pts[0:2]
        elif team_b_pts[2] == '/':
            team_b_pts = team_b_pts[0]
        elif team_b_pts[0] == '<':
            team_b_pts = 0
        team_b_pts = float(team_b_pts)

        date = game[game.find("date_game")+31:game.find("date_game")+48]
        if date[16] == '<':
            date = date[0:16]

        team_a_list.append(team_a)
        team_b_list.append(team_b)
        team_a_pts_list.append(team_a_pts)
        team_b_pts_list.append(team_b_pts)
        year_list.append(year)
        date_list.append(date)


matchups = pd.DataFrame({'team_a': team_a_list,
                         'team_a_pts' : team_a_pts_list,
                         'team_b' : team_b_list, 
                         'team_b_pts' : team_b_pts_list,
                         'year' : year_list,
                         'date' : date_list
})
matchups['pts_d'] = matchups['team_a_pts'] - matchups['team_b_pts']
matchups.tail(100)

# %%
df_list = []
date_list = []
team_a_list = []
team_b_list = []

for i in range(0, matchups.shape[0]):
    team_a = matchups['team_a'].iloc[i]
    team_b = matchups['team_b'].iloc[i]
    year = float(matchups['year'].iloc[i])
    date = matchups['date'].iloc[i]
    temp_a = teams[(teams['year'] == year) & (teams['team'] == team_a)].drop(['year', 'team'], axis=1)
    temp_b = teams[(teams['year'] == year) & (teams['team'] == team_b)].drop(['year', 'team'], axis=1)
    temp_d = (temp_a.iloc[0] - temp_b.iloc[0]).to_list()
    temp_d.append(matchups['year'].iloc[i])
    temp_d.append(matchups['pts_d'].iloc[i])
    date_list.append(date)
    team_a_list.append(team_a)
    team_b_list.append(team_b)
    df_list.append(temp_d) 
        
df = pd.DataFrame(df_list)
column_names = list(temp_a.columns.values)
column_names.append('year')
column_names.append('pts_d')

df.columns = column_names
df['date'] = date_list
df['team_a'] = team_a_list
df['team_b'] = team_b_list
df.head(30)

df.to_csv('/home/pi/wnba_predictions/matchup_stats.csv')


# %%



