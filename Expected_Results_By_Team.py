import pandas as pd


# imports CSV file of results from all World Cups and all other Info Generated from Expected_Results.py
df_to_use = pd.read_csv("Historical_World_Cup_Teams.csv")

# This creates a list of all teams that have competed in the World Cup
teams = df_to_use["Team"].unique()

# Lists for Summary statistics for each World Cup Team
wc_apps = []
start_avg_tpr = []
final_avg_tpr = []
total_prize_money = []
start_total_prize_money = []
final_total_prize_money = []
start_win_a_wc = []
start_make_a_final = []
start_make_a_sf = []
final_win_a_wc = []
final_make_a_final = []
final_make_a_sf = []
wc_wins = []
wc_final_apps = []
wc_sf_apps = []
start_exp_wc_wins = []
start_exp_final_apps = []
start_exp_sf_apps = []
final_exp_wc_wins = []
final_exp_final_apps = []
final_exp_sf_apps = []

# Finds the Summary Statistics for Each Team
for team in teams:
    team_tournament_data = df_to_use.where(df_to_use['Team'] == team).dropna()
    wc_apps.append(len(team_tournament_data['Year']))
    start_avg_tpr.append(team_tournament_data["Tournament Performance Rating (Starting Elo)"].mean())
    final_avg_tpr.append(team_tournament_data["Tournament Performance Rating (Final Elo)"].mean())
    total_prize_money.append(team_tournament_data['Prize Money'].sum())
    start_total_prize_money.append(team_tournament_data['Average Prize Money (Starting Elo)'].sum())
    final_total_prize_money.append(team_tournament_data['Average Prize Money (Final Elo)'].sum())
    start_win_a_wc_prob = 1
    start_make_a_final_prob = 1
    start_make_a_sf_prob = 1
    final_win_a_wc_prob = 1
    final_make_a_final_prob = 1
    final_make_a_sf_prob = 1
    for row, row_data in team_tournament_data.iterrows():
        start_win_a_wc_prob *= (1 - row_data['Win World Cup (Starting Elo)'])
        start_make_a_final_prob *= (1 - row_data['Make Final (Starting Elo)'])
        start_make_a_sf_prob *= (1 - row_data['Make Semifinals (Starting Elo)'])
        final_win_a_wc_prob *= (1 - row_data['Win World Cup (Starting Elo)'])
        final_make_a_final_prob *= (1 - row_data['Make Final (Final Elo)'])
        final_make_a_sf_prob *= (1 - row_data['Make Semifinals (Final Elo)'])
    start_win_a_wc.append(1 - start_win_a_wc_prob)
    start_make_a_final.append(1 - start_make_a_final_prob)
    start_make_a_sf.append(1 - start_make_a_sf_prob)
    final_win_a_wc.append(1 - final_win_a_wc_prob)
    final_make_a_final.append(1 - final_make_a_final_prob)
    final_make_a_sf.append(1 - final_make_a_sf_prob)
    wc_wins.append(len(team_tournament_data.where(team_tournament_data["Prize Money"] == 42).dropna()))
    wc_final_apps.append(len(team_tournament_data.where(team_tournament_data["Prize Money"] >= 30).dropna()))
    wc_sf_apps.append(len(team_tournament_data.where(team_tournament_data["Prize Money"] >= 25).dropna()))
    start_exp_wc_wins.append(team_tournament_data["Win World Cup (Starting Elo)"].sum())
    start_exp_final_apps.append(team_tournament_data["Make Final (Starting Elo)"].sum())
    start_exp_sf_apps.append(team_tournament_data["Make Semifinals (Starting Elo)"].sum())
    final_exp_wc_wins.append(team_tournament_data["Win World Cup (Final Elo)"].sum())
    final_exp_final_apps.append(team_tournament_data["Make Final (Final Elo)"].sum())
    final_exp_sf_apps.append(team_tournament_data["Make Semifinals (Final Elo)"].sum())

# Creates a DataFrame using lists of Summary Statistics
data = {'Team': teams, "World Cup Appearances": wc_apps, "Total Prize Money": total_prize_money,
        "Expected Total Prize Money (Starting Elo)": start_total_prize_money,
        "Expected Total Prize Money (Final Elo)": final_total_prize_money, "World Cups Won": wc_wins,
        "Final Appearances": wc_final_apps, "SF Appearances": wc_sf_apps,
        "Expected World Cup Wins (Starting Elo)": start_exp_wc_wins,
        "Expected Final Appearances (Starting Elo)": start_exp_final_apps,
        "Expected SF Appearances (Starting Elo)": start_exp_sf_apps,
        "Expected World Cup Wins (Final Elo)": final_exp_wc_wins,
        "Expected Final Appearances (Final Elo)": final_exp_final_apps,
        "Expected SF Appearances (Final Elo)": final_exp_sf_apps,
        "Probability of Winning a World Cup (Starting Elo)": start_win_a_wc,
        "Probability of Making a Final (Starting Elo)": start_make_a_final,
        "Probability of Making a Semifinal (Starting Elo)": start_make_a_sf,
        "Probability of Winning a World Cup (Final Elo)": final_win_a_wc,
        "Probability of Making a Final (Final Elo)": final_make_a_final,
        "Probability of Making a Semifinal (Final Elo)": final_make_a_sf,
        "Average Tournament Performance Rating (Starting Elo)": start_avg_tpr,
        "Average Tournament Performance Rating (Final Elo)": final_avg_tpr
        }

df = pd.DataFrame(data)

# Sorts the DataFrame by Total Prize Money Won
df = df.sort_values(by='Total Prize Money', ascending=False)

# exports Summary Statistics
df.to_csv("Overall_World_Cup_Team_Data.csv", index=False, header=True)
