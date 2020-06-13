# fuck node.js
# all my homies hate node.js
# i'll just use python to scrape the nba stats page

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import json
import time
import tkinter

driver_path = "D:/Desktop/Selenium/chromedriver"

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
def load_agg_jsons(years, dir='.'):
    return_dict = dict()
    for year in years:
        with open('NBAStats{}{}Agg.json'.format(year, year+1), 'r') as fp:
            return_dict['{}-{}'.format(year, year+1)] = json.load(fp)
    return return_dict

# test main function
# loads in the dictionary and then does stuff
# pick two stats and it'll plot everyone against them
def test1():
    full_stats_dict = load_agg_jsons(range(1996, 2020))
    


if __name__ == "__main__":
    mode = 1
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