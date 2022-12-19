import pandas as pd
import pickle
from scipy.stats import poisson

def main():
    # Load 2022 World Cup groups
    dict_table = pickle.load(open("dict_table.pkl", "rb"))
    # print(dict_table.keys())

    # Load CSV files with data
    df_historical_data = pd.read_csv("csv/clean_fifa_worldcup_historical_data.csv")
    df_fixture = pd.read_csv("csv/clean_fifa_worldcup_2022_fixtures.csv")
    # print(df_historical_data)

    # Compute team strength based on historical data
    df_team_strength = team_strength(df_historical_data)

    # Splitting fixtures into groups, knockout, quarter, etc...
    df_fixture_group_48 = df_fixture[:48].copy()
    df_fixture_knockout = df_fixture[48:56].copy()
    df_fixture_quarter = df_fixture[56:60].copy()
    df_fixture_semi = df_fixture[60:62].copy()
    df_fixture_final = df_fixture[62:].copy()

    # ----------------
    # GROUP STAGE
    # ----------------
    # Run all matches and update group tables
    for group in dict_table:
        # Get teams per group
        teams_in_group = dict_table[group]["Team"].values

        # Get all the matches for each group
        df_fixture_group_6 = df_fixture_group_48[df_fixture_group_48["home"].isin(teams_in_group)]

        # Simulate games for each group
        for _, row in df_fixture_group_6.iterrows():
            home, away = row["home"], row["away"]
            points_home, points_away = predict_points(home, away, df_team_strength)

            # Update points based on simulation
            dict_table[group].loc[dict_table[group]["Team"] == home, "Pts"] += points_home
            dict_table[group].loc[dict_table[group]["Team"] == away, "Pts"] += points_away
        
        # Sort table based on points (largest to smallest)
        dict_table[group] = dict_table[group].sort_values("Pts", ascending=False).reset_index()
        
        # Select only columns of interest (Team & Points)
        dict_table[group] = dict_table[group][["Team", "Pts"]]
        
        # Round points to avoid decimal values
        dict_table[group] = dict_table[group].round(0)

    # Show updated table
    # for group in dict_table:
    #     print(dict_table[group])
    #     print()

    # ----------------
    # KNOCKOUT STAGE
    # ----------------
    # Update knockout fixture with group winner and runner up
    for group in dict_table:
        group_winner = dict_table[group].loc[0, "Team"]
        runner_up = dict_table[group].loc[1, "Team"]

        df_fixture_knockout.replace({f"Winners {group}": group_winner}, inplace=True)
        df_fixture_knockout.replace({f"Runners-up {group}": runner_up}, inplace=True)
    
    # Add column for winner
    df_fixture_knockout["winner"] = "?"

    # Simulate knockout stage
    df_fixture_knockout = get_winner(df_fixture_knockout, df_team_strength)
    # print(df_fixture_knockout)

    # ----------------
    # QUARTER FINAL
    # ----------------
    # Update quarter-finals table
    df_fixture_quarter = update_table(df_fixture_knockout, df_fixture_quarter)
    # print(df_fixture_quarter)

    # Get quarter finals winners
    df_fixture_quarter = get_winner(df_fixture_quarter, df_team_strength)

    # ----------------
    # SEMI-FINAL
    # ----------------
    df_fixture_semi = update_table(df_fixture_quarter, df_fixture_semi)
    # print(df_fixture_semi)

    # Get semi-finals winners
    df_fixture_semi = get_winner(df_fixture_semi, df_team_strength)

    # ----------------
    # FINAL
    # ----------------
    df_fixture_final = update_table(df_fixture_semi, df_fixture_final)
    df_fixture_final.drop(df_fixture_final.index[[0]], inplace=True)
    # print(df_fixture_final)

    # Get semi-finals winners
    df_fixture_final = get_winner(df_fixture_final, df_team_strength)
    print(df_fixture_final)


# --------------------------------------------
# Function to calculate team strength
# --------------------------------------------
def team_strength(historical_data):
    """
    Compute each team's strength based on historical data.

    Input:
        - historical_data: DataFrame with all the results from previous World Cups
    
    Return:
        - DataFrame with average 'GoalsScored' and 'GoalsConceded'
          per team in all previous World Cups. This will be used as a measure of
          strength for predictions
    """
    # Split historical DataFrame into df_home and df_away
    df_home = historical_data[["HomeTeam", "HomeGoals", "AwayGoals"]]
    df_away = historical_data[["AwayTeam", "HomeGoals", "AwayGoals"]]

    # Rename columns so we have standard names
    df_home = df_home.rename(columns={
                "HomeTeam": "Team",
                "HomeGoals": "GoalsScored",
                "AwayGoals": "GoalsConceded",
            },
        )
    
    df_away = df_away.rename(columns={
                "AwayTeam": "Team",
                "HomeGoals": "GoalsConceded",
                "AwayGoals": "GoalsScored",
            },
        )

    # Concatenate df_home and df_away with
    # Compute average 'GoalsScored' and 'GoalsConceded' per team
    df_team_strength = pd.concat([df_home, df_away], ignore_index=True).groupby("Team").mean()

    # Return DataFrames
    return df_team_strength


# --------------------------------------------
# Function to predict points based on team strength
# --------------------------------------------
def predict_points(home, away, team_strength):
    """
    Simulates a game between 'home' team and 'away' team. If team is not listed
    in team_strength, then both teams receive zero points.

    Input:
        - home: Name of home team
        - away: Name of away team
        - team_strength: DataFrame with each team's strength

    Return:
        - points_home: Points awarded to home team based on simulation 
        - points_away: Points awarded to away team based on simulation
    """
    if home in team_strength.index and away in team_strength.index:
        # Lambda = GoalsScored * GoalsConceded -> Benefit teams that score more goals, and
        #                                         penalize those teams that receive many goals
        lamb_home = team_strength.at[home, "GoalsScored"] * team_strength.at[away, "GoalsConceded"]
        lamb_away = team_strength.at[away, "GoalsScored"] * team_strength.at[home, "GoalsConceded"]

        # Initialize probabilities
        prob_home, prob_away, prob_draw = 0, 0, 0

        # Compute poisson probability of each event (max. number of goals per team per game = 10)
        for x in range(0, 11):      # Number goals home team
            for y in range(0, 11):  # Number goals away team
                # Compute Poisson probability
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                if x == y:
                    prob_draw += p
                elif x > y:
                    prob_home += p
                else:
                    prob_away += p
        
        points_home = 3 * prob_home + prob_draw
        points_away = 3 * prob_away + prob_draw
        return (points_home, points_away)
    else:
        return (0, 0)


# --------------------------------------------
# Function to predict winners in advanced stages
# --------------------------------------------
def get_winner(df_fixture_updated, team_strength):
    """"
    Determine the winners in knockout and later stages of the tournament

    Input:
        - df_fixture_updated: DataFrame with the fixtures for futrue rounds
        - team_strength: DataFrame with each team's strength

    Return:
        - Updated DataFrame with winning teams
    """
    for idx, row in df_fixture_updated.iterrows():
        # Get match from DataFrame
        home, away = row["home"], row["away"]

        # Simulate game
        points_home, points_away = predict_points(home, away, team_strength)

        # Define which team wins the match
        if points_home > points_away:
            winner = home
        else:
            winner = away

        # Update DataFrame
        df_fixture_updated.loc[idx, "winner"] = winner 
    
    # Return Updated DataFrame
    return df_fixture_updated


# --------------------------------------------
# Function to update tables with winners from previous rounds
# --------------------------------------------
def update_table(df_fixture_round1, df_fixture_round2):
    for idx, row in df_fixture_round1.iterrows():
        winner = df_fixture_round1.loc[idx, "winner"]
        match = df_fixture_round1.loc[idx, "score"]
        df_fixture_round2.replace({f"Winners {match}": winner}, inplace=True)
    df_fixture_round2["winner"] = "?"
    return df_fixture_round2


# --------------------------------------------
# Run 'main' function:
# --------------------------------------------
if __name__ == "__main__":
    main()