from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

def main():
    # Create array with World Cup years
    years = np.arange(1930, 2022, 4)
    years = np.delete(years, [3, 4])
    # print(years)

    # Get matches of all previous World Cups
    # BE AWARE!!!!: Some World Cups are formatted differently, so with this
    # method is not possible to retrieve all the data, for instance, check
    # DataFrame for years 1982.
    # c03_get_missing_data.py is used to retieve missing data 
    
    # Use list comprehension to build Dataset
    fifa = [get_matches(year) for year in years]

    # Concatenate all the DataFrames in 'fifa'
    df_fifa = pd.concat(fifa, ignore_index=True)
    df_fifa.to_csv("fifa_worldcup_historical_data.csv", index=False)
    # print(df_fifa)

    # Get fixtures for 2022 World Cup
    df_fixtures = get_matches(2022)
    df_fixtures.to_csv("fifa_worldcup_2022_fixtures.csv", index=False)
    # print(df_fixtures)


# --------------------------------------------
# Function to retrieve info from Web
# --------------------------------------------
def get_matches(year):
    # Retrieve data from web
    if year == 2022:
        # World Cup was already played when I created this file, so I'm retrieving
        # data from an archive (only fixtures, no results)
        response = requests.get(f"https://web.archive.org/web/20221115040351/https://en.wikipedia.org/wiki/2022_FIFA_World_Cup")
    else:
        response = requests.get(f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup")
    
    content = response.text
    soup = BeautifulSoup(content, "lxml")

    # Start scraping data
    matches = soup.find_all("div", class_="footballbox")

    # Initialize lists
    home = []
    score = []
    away = []

    for match in matches:
        home.append(match.find("th", class_="fhome").get_text())
        score.append(match.find("th", class_="fscore").get_text())
        away.append(match.find("th", class_="faway").get_text())

    # Create dict
    dict_footbal = {"home": home, "score": score, "away": away}

    # Create dataFrame
    df_football = pd.DataFrame(dict_footbal)
    df_football["year"] = year

    return df_football


# --------------------------------------------
# Run 'main' function
# --------------------------------------------
if __name__ == "__main__":
    main()