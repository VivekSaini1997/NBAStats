# fuck node.js
# all my homies hate node.js
# i'll just use python to scrape the nba stats page

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import json
import time
import tkinter
from matplotlib import pyplot as plt


driver_path = "D:/Desktop/Selenium/chromedriver"

team_colors = {
    # interior exterior
    'SEA': ('#FFC200', '#00653A'),
    'ATL': ('#FFFFFF', '#e03a3e'),
    'BKN': ('#00a55c', '#000000'),
    'BOS': ('#FFFFFF', '#000000'),
    'CHA': ('#00788c ','#1d1160'),
    'CHI': ('#CE1141', '#000000'),
    'CLE': ('#6f2633', '#ffb81c'),
    'DAL': ('#', '#'),
    'DEN': ('#', '#'),
    'DET': ('#', '#'),
    'GSW': ('#', '#'),
    'HOU': ('#', '#'),
    'IND': ('#', '#'),
    'LAC': ('#', '#'),
    'LAL': ('#', '#'),
    'MEM': ('#', '#'),
    'MIA': ('#', '#'),
    'MIL': ('#', '#'),
    'MIN': ('#', '#'),
    'NOP': ('#', '#'),
    'NYK': ('#', '#'),
    'OKC': ('#', '#'),
    'ORL': ('#', '#'),
    'PHI': ('#', '#'),
    'PHX': ('#', '#'),
    'POR': ('#', '#'),
    'SAC': ('#', '#'),
    'SAS': ('#', '#'),
    'TOR': ('#', '#'),
    'UTA': ('#', '#'),
    'WAS': ('#', '#'),
}

# just test the request first
def main():
    res = requests.get("https://stats.nba.com/leaders/?Season=2019-20&SeasonType=Regular%20Season")
    # using beatiful soup to parse html
    soup = bs(res.text, features='html.parser')

    print(soup)

# nope, need selenium rip

# try to send find the dialog box
# only execute "attempts" times at most
def get_box_with_attempts(driver, attempts=5):
    attempt = 0
    while attempt < attempts:
        try:
            driver.find_elements_by_class_name("stats-table-pagination__select")[0]
            driver.send_keys('All')
            return
        except:
            print('Failed to find box, retrying after 500ms')
            attempt += 1
    raise IndexError("No Box Found.")

# because i don't feel like scraping every single time, load in results from API from time to time
def main3():
    # load in the files
    pass

# load in the stats for all the players in a given year
# goes through all of specified categories to do this
# writes the results to a json 
def load_urls(driver, year, categories):
    # the dict used to store the stats for this year
    player_stats_dict = dict()
    print(categories)
    for category in categories:
        # fetch the required web page
        url = 'https://stats.nba.com/players/{}/?Season={}-{:02}&SeasonType=Regular%20Season'.format(category, year, (year + 1) % 100)
        print(url)
        driver.get(url)
        # find the input box and set it 
        box_element = driver.find_elements_by_class_name("stats-table-pagination__select")[0]
        box_element.send_keys('All')        
        # now get the stats for each player
        # the list duplicates, we want the first half
        players = driver.find_elements_by_css_selector("tr[data-ng-repeat]")
        players = players[:len(players)//2]
        # also get the names of each of the recorded statistics for this uel
        stat_names = driver.find_elements_by_css_selector("th[cf]")
        stat_names = [n.text for n in stat_names][1:-2]
        # add stats to the dict as needed
        # indexed by player name first
        # then a specific stat for said player 
        for player in players:
            # for some reason there's a player with no name in the NBA stats database
            # this try catch is to ignore him because he breaks the code lmao
            try:
                _, player_name, player_stats = player.text.split('\n')
            except ValueError:
                continue
            if player_name in player_stats_dict:
                for stat_name, player_stat in zip(stat_names, player_stats.split(' ')):
                    player_stats_dict[player_name][stat_name] = player_stat
            else:
                player_stats_dict[player_name] = dict(zip(stat_names, player_stats.split(' ')))
    # once the dict has been populated, write it to a json
    with open('NBAStats{}{}Agg.json'.format(year, year+1), 'w+') as fp:
        json.dump(player_stats_dict, fp)

# load the stats from a set of JSON files
# specify the years you want with a range(startyear, endyear)
# and the directory where the files are located
def load_agg_jsons(years=range(1996, 2020), directory='fixed_json'):
    return_dict = dict()
    for year in years:
        with open('{}/NBAStats{}{}Agg.json'.format(directory, year, year+1), 'r') as fp:
            return_dict['{}-{}'.format(year, year+1)] = json.load(fp)
    return return_dict

# test main function
# loads in the dictionary and then does stuff
# pick two stats and it'll plot everyone against them
def test1():
    full_stats_dict = load_agg_jsons(range(1996, 2020), 'fixed_json')

    # our test is 1996-1997 season, DREB vs OREB
    season_dict = full_stats_dict['1996-1997']
    dreb = list()
    oreb = list()
    name = list()
    # plotting code
    for player in season_dict:
        player_dict = season_dict[player]
        dreb.append(player_dict['DREB'])
        oreb.append(player_dict['OREB'])
        name.append(player)
 
    fig, ax = plt.subplots()
    sc = plt.scatter(dreb, oreb)
    plt.show()



# make it so that numeric stats are represented as such
# instead of as strings in the json files
def fix_json():
    years = range(1996, 2020)
    for year in years:
        fname = 'NBAStats{}{}Agg.json'.format(year, year+1)
        with open(fname, 'r') as readfile:
            dict_ = json.load(readfile)
        for player in dict_:
            for stat in dict_[player]:
                try:
                    dict_[player][stat] = float(dict_[player][stat])
                except:
                    pass
        with open('fixed_json/{}'.format(fname), 'w+') as writefile:
            json.dump(dict_, writefile)

#list all of the teams in the 2019-20 season
def list_new_teams():
    teams = list()
    stats = load_agg_jsons()

    stats = stats['2019-2020']
    for player in stats:
        teams.append(stats[player]['TEAM'])

    teams = list(set(teams))
    for team in sorted(teams):
        print('\'{}\': (\'#\', \'#\'),'.format(team))
    print(len(teams))




if __name__ == "__main__":
    mode = 4
    if mode == 0:
    # code to run the scraper
        categories = [
            'traditional',
            'advanced',
            ]
        driver = webdriver.Chrome(executable_path=driver_path)
        driver.implicitly_wait(15)
        years = reversed(range(1996, 1998))
        for year in years:
            load_urls(driver, year, categories)
    elif mode == 1:
        returned_dict = load_agg_jsons(range(1996, 2020))
        print(returned_dict['1996-1997']['Dennis Rodman'])
    elif mode == 2:
        fix_json()
    elif mode == 3:
        test1()
    elif mode == 4:
        list_new_teams()