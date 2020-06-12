# fuck node.js
# all my homies hate node.js
# i'll just use python to scrape the nba stats page

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import json
import time

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

def main2():
    driver = webdriver.Chrome(executable_path=driver_path)

    driver.get('https://stats.nba.com/players/advanced/')

    # attempts = 0
    # while attempts < 5:
    #     try:
    #         driver.get("https://stats.nba.com/players/advanced/")
    #         break
    #     except:
    #         print('Failed once, retrying after 500ms')
    #         time.sleep(500)
    #         attempts += 1
    # get_with_attempts


    # make sure you're looking at all of the players
    box = driver.find_elements_by_class_name("stats-table-pagination__select")[0]
    box.send_keys('All')

    # find the players
    # players = driver.find_elements_by_class_name('player')
    # print(players[0].text, players[1].text)
    # playertexts = [ p.text for p in players ]
    # for player in playertexts:
    #     print(player)
    # print(len(playertexts))

    # maybe find the entire row instead?
    row = driver.find_elements_by_css_selector("tr[data-ng-repeat]")
    
    # also find the row that specifies the row?
    names = driver.find_elements_by_css_selector("th[cf]")
    # the elements duplicate, we only need the first half of the list
    row = row[:len(row)//2]

    # for elem in row:
    #     print(elem.text)

    header2 = [n.text for n in names][1:-2]

    # for name in names:
    
    playerdict = dict()

    # create a dict of dicts for all of the players
    # indexed by player name first
    # then a specific stat for said player 
    for player in row:
        smth = player.text.split('\n')
        print(smth[2])
        playerdict[smth[1]] = dict(zip(header2, smth[2].split(' ')))

    # now try to load the traditional stats

    # with open('NBA2019_2020_adv.json', 'w+') as f:
    #     json.dump(playerdict, f)
    # print(row[0].text.split('\n')[2])
    
# because i don't feel like scraping every single time, load in results from API from time to time
def main3():
    # load in the files
    pass
# load in the advanced stats for a given year
def load_adv(year):

    return

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

if __name__ == "__main__":
    categories = [
        'traditional',
        'advanced',
        ]
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.implicitly_wait(15)
    years = reversed(range(1996, 1998))
    for year in years:
        load_urls(driver, year, categories)