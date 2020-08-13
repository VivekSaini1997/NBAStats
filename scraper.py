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
    'ATL': ('#FFFFFF', '#E03A3E'),
    'BKN': ('#FFFFFF', '#000000'),
    'BOS': ('#007A33', '#000000'),
    'CHA': ('#00788C ','#1D1160'),
    'CHH': ('#00788C ','#1D1160'),
    'CHI': ('#CE1141', '#000000'),
    'CLE': ('#000000', '#860038'),
    'DAL': ('#00538C', '#B8C4CA'),
    'DEN': ('#0E2240', '#FEC524'),
    'DET': ('#C8102E', '#1D42BA'),
    'GSW': ('#1D428A', '#FFC72C'),
    'HOU': ('#CE1141', '#000000'),
    'IND': ('#FDBB30', '#002D62'),
    'LAC': ('#1D428A', '#C8102E'),
    'LAL': ('#FDB927', '#552583'),
    'MEM': ('#5D76A9', '#12173F'),
    'MIA': ('#98002E', '#F9A01B'),
    'MIL': ('#EEE1C6', '#00471B'),
    'MIN': ('#236192', '#0C2340'),
    'NJN': ('#CD1041', '#002A60'),
    'NOH': ('#00778B ','#280071'),
    'NOK': ('#00778B ','#280071'),
    'NOP': ('#0C2340', '#85714D'),
    'NYK': ('#F58426', '#006BB6'),
    'OKC': ('#EF3B24', '#007AC1'),
    'ORL': ('#0077C0', '#000000'),
    'PHI': ('#006BB6', '#ED174C'),
    'PHX': ('#E56020', '#F9AD1B'),
    'POR': ('#E03A3E', '#000000'),
    'SAC': ('#5A2D81', '#63727A'),
    'SAS': ('#C4CED4', '#000000'),
    'SEA': ('#00653A', '#FFC200'),
    'TOR': ('#000000', '#CE1141'),
    'UTA': ('#002B5C', '#00471B'),
    'VAN': ('#00B2A9', '#BC7844'),    
    'WAS': ('#002B5C', '#E31837'),
    'WSB': ('#002B5C', '#E31837'),
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
        try:
            with open('{}/NBAStats{}{}Agg.json'.format(directory, year, year+1), 'r') as fp:
                return_dict['{}-{}'.format(year, year+1)] = json.load(fp)
        except:
            pass
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

# return a json that gets the description of each stat
def get_stats_glossary():
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.implicitly_wait(15)
    url = "https://stats.nba.com/help/glossary"
    driver.get(url)
    # get each stat
    stats = driver.find_elements_by_class_name('stats-glossary-page__item')
    vals = dict()
    for stat in stats:
        stat_lines = stat.text.split('\n')
        d = dict()
        d['Name'] = ''
        d['Definition'] = ''
        d['Type'] = ''
        d['Contexts'] = list()
        _type = ''
        for word in stat_lines[1].split():
            if word in ['Name', 'Definition', 'Type', 'Contexts']:
                _type = word
            elif _type == 'Contexts':
                d['Contexts'].append(word)
            else:
                d[_type] += '{} '.format(word)
        # print('-----')
        vals[stat_lines[0].lower()] = d
    with open("Stats.json", 'w+') as f:
        json.dump(vals, f)
    print('All done')


if __name__ == "__main__":
    mode = 5
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
    elif mode == 5:
        get_stats_glossary()