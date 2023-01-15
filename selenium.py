from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Check out this post for an explanation of the below [basic] code: https://bowtiedbettor.substack.com/p/build-your-first-odds-scraper

"""
Set up a selenium/webdriver session
"""
# Find chromedriver on your computer, copy full path and paste here
path = "PATH_TO_CHROMEDRIVER" 
driver = webdriver.Chrome(path)


"""
Call the relevant website
"""
driver.get("https://www.unibet.com/betting/sports/filter/baseball/mlb/all/matches")
time.sleep(1)


"""
Find the 'Today' element and store it
"""
today_object = driver.find_element(By.CLASS_NAME, "_79bb0")
time.sleep(1)


"""
Find all the games and store them in a list
"""
games = today_object.find_elements(By.CLASS_NAME, "f9aec._0c119.bd9c6")


"""
Loops through the games and prints the relevant data
"""
for game in games:
    team_names = game.find_elements(By.CLASS_NAME, "_6548b")
    team_names_list = []
    for team in team_names:
        team_names_list.append(team.get_attribute("textContent"))

    home_name = team_names_list[0]
    away_name = team_names_list[1]

    odds = game.find_element(By.CLASS_NAME, "bb419")
    home_odds = odds.get_attribute("textContent")[0:4]
    away_odds = odds.get_attribute("textContent")[4:8]

    print(home_name, home_odds)
    print(away_name, away_odds)

    print("")

driver.quit()
