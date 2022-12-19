import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

# Start selenium (to control web browser)
path = "/home/gaortiz/Documents/notebooks/worldcup"
service = Service(executable_path=path)
driver = webdriver.Firefox(service=service)


def main():
    # Create array with World Cup years
    years = np.arange(1930, 2022, 4)
    years = np.delete(years, [3, 4])
    # print(years)

    # Use list comprehension to build Dataset
    fifa = [get_misssing_data(year) for year in years]
    
    # Close selenium service
    driver.quit()

    # Concatenate all the DataFrames in 'df_fifa'
    df_fifa = pd.concat(fifa, ignore_index=True)
    df_fifa.to_csv("fifa_worldcup_missing_data.csv", index=False)


# Define function to retrieve info from Web
def get_misssing_data(year):
    # Prepare selenium driver
    driver.get(f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup")

    # Find pattern in webpages and store results
    matches = driver.find_elements(by='xpath', value='//td[@align="right"]/.. | //td[@style="text-align:right;"]/..')
    # matches = driver.find_elements(by='xpath', value='//tr[@style="font-size:90%"]')

    # Initialize lists
    home = []
    score = []
    away = []
    for match in matches:
        home.append(match.find_element(by='xpath', value='./td[1]').text)
        score.append(match.find_element(by='xpath', value='./td[2]').text)
        away.append(match.find_element(by='xpath', value='./td[3]').text)

    # Create dict
    dict_football = {'home': home, 'score': score, 'away': away}

    # Create dataFrame
    df_football = pd.DataFrame(dict_football)
    df_football['year'] = year

    return df_football


# Run 'main' function:
if __name__ == "__main__":
    main()