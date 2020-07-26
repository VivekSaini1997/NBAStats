# these are various other functions for visualization instead of scraping

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import scraper

# test main function
# loads in the dictionary and then does stuff
# pick two stats and it'll plot everyone against them
def visualize():
    full_stats_dict = scraper.load_agg_jsons(range(1996, 2020), 'fixed_json')

    # our test is 1996-1997 season, DREB vs OREB
    season_dict = full_stats_dict['1996-1997']
    dreb = list()
    oreb = list()
    name = list()
    logos = list()

    root = 'logos/'

    # plotting code
    for player in season_dict:
        player_dict = season_dict[player]
        dreb.append(player_dict['DREB'])
        oreb.append(player_dict['OREB'])
        name.append(player)
        logos.append('{}{}.gif'.format(root, player_dict['TEAM']))


    fig, ax = plt.subplots()
    sc = ax.scatter(dreb, oreb)

    for x0, y0, path in zip(dreb, oreb, logos):
        ab = AnnotationBbox(OffsetImage(plt.imread(path)), (x0, y0), frameon=False)
        ax.add_artist(ab)


    plt.show()

if __name__ == "__main__":
    visualize()


