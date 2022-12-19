import numpy as np
import pandas as pd
import re

def main():
    # Load data from CSV files
    df_historical_data = pd.read_csv("csv/fifa_worldcup_historical_data.csv")
    df_fixture = pd.read_csv("csv/fifa_worldcup_2022_fixtures.csv")
    df_missing_data = pd.read_csv("csv/fifa_worldcup_missing_data.csv")
    
    # Clean df_fixture (remove leading and trailing whitespaces)
    df_fixture["home"] = df_fixture["home"].str.strip()
    df_fixture["away"] = df_fixture["away"].str.strip()

    # Clean df_missing_data and adding it to df_historical_data
    # Drop null data
    df_missing_data.dropna(inplace=True)
    # print(df_missing_data)
    # print()
    # print(df_missing_data[df_missing_data["home"].isnull()])

    # Concatenate df_missing_data with df_historical_data
    df_historical_data = pd.concat([df_historical_data, df_missing_data], ignore_index=True)
    # print(df_historical_data)

    # Avoid for duplicate data, and sort data by 'year'
    df_historical_data.drop_duplicates(inplace=True)
    df_historical_data.sort_values("year", inplace=True)
    # print(df_historical_data)

    # Clean df_historical_data
    # Manually delete match with walk-over (outlier)
    # print(df_historical_data[df_historical_data["home"].str.contains("Sweden") &
    #                          df_historical_data["away"].str.contains("Austria")])
    delete_idx = df_historical_data[df_historical_data["home"].str.contains("Sweden") &
                                    df_historical_data["away"].str.contains("Austria")].index
    
    df_historical_data.drop(index=delete_idx, inplace=True)

    # Use Regex to delete unnecessary info in 'score' column
    # regex_pat = re.compile(r" \(.*\)")
    regex_pat = re.compile(r"[^\d-]")
    df_historical_data["score"] = df_historical_data["score"].str.replace(regex_pat, "", regex=True)
    # print(df_historical_data)

    # Remove leading and trailing whitespaces
    df_historical_data["home"] = df_historical_data["home"].str.strip()
    df_historical_data["score"] = df_historical_data["score"].str.strip()
    df_historical_data["away"] = df_historical_data["away"].str.strip()
    # print(df_historical_data)

    # Split 'score' column into 'home_score' and 'away_score'. Delete 'score' column
    df_historical_data[["HomeGoals", "AwayGoals"]] = df_historical_data["score"].str.split("-", expand=True)
    df_historical_data.drop("score", axis=1, inplace=True)
    # print(df_historical_data)

    # Rename columns and change data types (dtypes)
    df_historical_data.rename(columns={
            "home": "HomeTeam",
            "away": "AwayTeam",
            "year": "Year",
        },
    inplace=True)
    df_historical_data = df_historical_data.astype({
            "HomeGoals": int,
            "AwayGoals": int,
            "Year": int,
        }
    )

    # Create a new column 'TotalGoals'
    df_historical_data["TotalGoals"] = df_historical_data["HomeGoals"] + \
                                       df_historical_data["AwayGoals"]
    # print(df_historical_data)

    # Export clean DataFrame
    # df_historical_data.to_csv("csv/clean_fifa_worldcup_historical_data.csv", index=False)
    # df_fixture.to_csv("csv/clean_fifa_worldcup_2022_fixtures.csv", index=False)

    # ------------------------
    # EXTRA VERIFICATIONS
    # ------------------------
    # Create array with World Cup years
    years = np.arange(1930, 2022, 4)
    years = np.delete(years, [3, 4])

    # Check number of matches per World Cup
    for year in years:
        print(year, len(df_historical_data[df_historical_data["Year"] == year]))


# Run 'main' function:
if __name__ == "__main__":
    main()