# NBAStats

## Summary
A visualization tool to compare various stats from the 1996-97 NBA Season to the 2019-20 season, prior to the bubble.

## Dependancies
 - Python 3.7+
 - pip
 
## Installation
Install all of the required dependancies on your system using pip with the following command (from the NBAStats directory).
```
pip install -r requirements.txt
```
This will install the following python libraries:
  - PyQt5
  - pyqtgraph
  - numpy
  - selenium
  - requests
  - beautifulsoup4
 
## Usage
Open up the GUI by running
```
python visualization.py
```
From there, you can start to compare players on a XY grid with different stats as axes. Each of the circles on the plot represents a different player. Hovering over the circle will show the name of the player and their statistical performance in the selected stats overlayed over their respective team logo. In addition to the circles, there is a line drawn on the plot representing the list of best fit. The degree of this line can be changed by adjusting the slider locating underneath the plot on the right side.

### Changing stats
You can change which stats are being compared by picking a different stat using the dropdown menu near the respective axis. If you don't know what a particular stat means, hover over it in the dropdown menu to see a more detailed description of said stat. You can also change the season that is being represented by using the dropdown at the top.

### Filtering based on stats
You can filter certain players out when plotting using filters. This can be typing a condition using Python syntax into the white bar at the bottom of the screen and pressing "Enter". For example, to keep only filters who have more than 5 points and 2 assists, we would type:
```
PTS > 5 and AST > 2
```
To keep all players that played for either the Boston Celtics (BOS) or the Miami Heat (MIA), we could type:
```
team in ('BOS', 'MIA')
```
or:
```
(team == 'BOS') or (team == 'MIA')
```
where the parantheses are optional and for example purposes only

The supported symbols are:
 - Any word that appears in the dropdown menu
 - `>`, `<`, `==`, `<=`, `>=`, `and`, `or`, `not`, `in`, `(`, `)`, and `,`
 - The word 'team' and the abbreviations of any team that has played since '96-'97

### Navigating
Zoom in on the plot by scrolling up and zoom out by scrolling down. Left click and drag to move the plot around. Reset the plot by clicking the small 'A' in the bottom left corner of the plot
