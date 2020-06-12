/*
    a webscraper for NBA data using selenium
*/
// import libraries
const {Builder, By, Key, until} = require('selenium-webdriver');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  

// create an async request
async function example() {
    let driver = await new Builder().forBrowser('chrome').build();
    
    try {
        // send a GET request to an NBA stats website
        await driver.get('https://stats.nba.com/leaders/');
        
        driver.wait(() => {})
          
        // now force all players stats onto screen
        res = await driver.findElement(By.className('stats-table-pagination__select ng-pristine ng-valid ng-not-empty ng-touched'));
        console.log(res)

        await sleep(10000);
    } 
    finally {
        driver.quit();
    }


}


example()
