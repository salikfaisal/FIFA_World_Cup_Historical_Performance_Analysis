import random
import statistics
import pandas as pd

# imports CSV file of results from all World Cups
df = pd.read_csv("Historical_World_Cup_Teams.csv")

# this function returns a simulation of the results of a game given the elo ratings of the two teams
def match_result(team_1_elo, team_2_elo):
    # uses the elo formula to get the two-outcome win probability
    team_1_wl = 1 / (10 ** ((team_2_elo - team_1_elo) / 400) + 1)
    # gets the average goal difference expected between the two sides
    # if two sides have an equal rating the probabilities are: 35% Team 1 win, 30% draw, 35% Team 2 win
    team_1_margin_mean = statistics.NormalDist(0, 1.3).inv_cdf(team_1_wl)
    # the goal difference as a result of a random simulation
    team_1_margin = round(statistics.NormalDist(team_1_margin_mean, 1.3).inv_cdf(random.random()))
    # the goal probability distribution from 1826 matches in the 2020-21 season in Europe's top 5 leagues
    goal_prob = [0.25985761226725085, 0.3417305585980285, 0.22343921139101863, 0.1119934282584885, 0.0443592552026287,
                 0.014786418400876232, 0.0024644030668127055, 0.0008214676889375684, 0.0002738225629791895,
                 0.0002738225629791895]
    gp_list = []
    if abs(team_1_margin) > 9:
        winning_goal_count = abs(team_1_margin)
        losing_goal_count = 0
    else:
        gp_list = goal_prob[abs(team_1_margin):]
        total = sum(gp_list)
        cum = 0
        for goal_count, goal_probability in enumerate(gp_list):
            gp_list[goal_count] = goal_probability / total
        goal_result = random.random()
        for gc, gp in enumerate(gp_list):
            cum += gp
            if goal_result < cum:
                winning_goal_count = gc + abs(team_1_margin)
                winning_goal_count = gc + abs(team_1_margin)
                losing_goal_count = winning_goal_count - abs(team_1_margin)
                break
    if team_1_margin >= 0:
        home_goals = winning_goal_count
        away_goals = home_goals - team_1_margin
    else:
        away_goals = winning_goal_count
        home_goals = away_goals + team_1_margin
    return [home_goals, away_goals]


# This function returns the Elo Rating for a Country in a particular World Cup Year
def team_wc_rating(is_starting, team, year):
    team_tournament_data = df.where(df['Team'] == team).where(df['Year'] == year).dropna()
    team_tournament_data = team_tournament_data.reset_index()
    if is_starting:
        rating = team_tournament_data.at[0, 'Starting Rating']
    else:
        rating = team_tournament_data.at[0, 'Final Rating']
    return rating


class world_cup_simulation:
    def __init__(self, is_starting, year):
        self.is_starting = is_starting
        self.year = year

    def simulation_1930(self):
        is_starting = self.is_starting
        year = self.year
        groups = [['Argentina', 'Chile', 'France', 'Mexico'], ['Serbia', 'Brazil', 'Bolivia'],
                  ['Uruguay', 'Romania', 'Peru'], ['United States', 'Paraguay', 'Belgium']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        semifinalists = []
        for group in groups:
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, 1930)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Group Winners to the list of Semifinalists
            semifinalists.append(group_standings[0][0])
        # Semifinal Stage
        # Creates the Semifinal Matchups
        sf_matchups = [[semifinalists[0], semifinalists[3]], [semifinalists[1], semifinalists[2]]]
        finalists = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, 1930)
            team_2_elo = team_wc_rating(is_starting, team_2, 1930)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                finalists.append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                finalists.append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                replay_score = match_result(team_1_elo, team_2_elo)
                if replay_score[0] > replay_score[1]:
                    finalists.append(team_1)
                elif replay_score[1] > replay_score[0]:
                    finalists.append(team_2)
                else:
                    finalists.append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # World Cup Final Stage
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, 1930)
        team_2_elo = team_wc_rating(is_starting, team_2, 1930)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 1
        team_2_standings[4] += 1
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            replay_score = match_result(team_1_elo, team_2_elo)
            if replay_score[0] > replay_score[1]:
                team_1_standings[4] += 1
            elif replay_score[1] > replay_score[0]:
                team_2_standings[4] += 1
            else:
                champion = finalists[random.randrange(0, 2)]
                if champion == team_1:
                    team_1_standings[4] += 1
                else:
                    team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1934_and_1938(self):
        is_starting = self.is_starting
        year = self.year
        if year == 1934:
            r16_matchups = [['Italy', 'United States'], ['Spain', 'Brazil'], ['Austria', 'France'],
                            ['Hungary', 'Egypt'],
                            ['Czech Republic', 'Romania'], ['Switzerland', 'Netherlands'], ['Germany', 'Belgium'],
                            ['Sweden', 'Argentina']]
        elif year == 1938:
            r16_matchups = [['Italy', 'Norway'], ['France', 'Belgium'], ['Brazil', 'Poland'],
                            ['Czech Republic', 'Netherlands'], ['Hungary', 'Indonesia'], ['Switzerland', 'Germany'],
                            'Sweden', ['Cuba', 'Romania']]
        full_tournament_standings = {}
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        # Round of 16 Stage
        quarterfinal_matchups = [[], [], [], []]
        for matchup_number, matchup in enumerate(r16_matchups):
            qf_match = matchup_number // 2
            if matchup == 'Sweden':
                quarterfinal_matchups[qf_match].append('Sweden')
                full_tournament_standings.update({'Sweden': [0, 0, 0, 0, 0]})
                continue
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = [0, 0, 0, 0, 0]
            team_2_standings = [0, 0, 0, 0, 0]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            if score[0] > score[1]:
                team_1_standings[0] += 2
                quarterfinal_matchups[qf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                quarterfinal_matchups[qf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                replay_score = match_result(team_1_elo, team_2_elo)
                if replay_score[0] > replay_score[1]:
                    quarterfinal_matchups[qf_match].append(team_1)
                elif replay_score[1] > replay_score[0]:
                    quarterfinal_matchups[qf_match].append(team_2)
                else:
                    quarterfinal_matchups[qf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Quarterfinal Stage
        sf_matchups = [[], []]
        for matchup_number, matchup in enumerate(quarterfinal_matchups):
            sf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                sf_matchups[sf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                sf_matchups[sf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                replay_score = match_result(team_1_elo, team_2_elo)
                if replay_score[0] > replay_score[1]:
                    sf_matchups[sf_match].append(team_1)
                elif replay_score[1] > replay_score[0]:
                    sf_matchups[sf_match].append(team_2)
                else:
                    sf_matchups[sf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Semifinal Stage
        finalists = []
        third_place_playoff = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                finalists.append(team_1)
                third_place_playoff.append(team_2)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                finalists.append(team_2)
                third_place_playoff.append(team_1)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                replay_score = match_result(team_1_elo, team_2_elo)
                if replay_score[0] > replay_score[1]:
                    finalists.append(team_1)
                    third_place_playoff.append(team_2)
                elif replay_score[1] > replay_score[0]:
                    finalists.append(team_2)
                    third_place_playoff.append(team_1)
                else:
                    finalist = matchup[random.randrange(0, 2)]
                    finalists.append(finalist)
                    if team_1 == finalist:
                        third_place_playoff.append(team_2)
                    else:
                        third_place_playoff.append(team_1)
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            replay_score = match_result(team_1_elo, team_2_elo)
            if replay_score[0] > replay_score[1]:
                team_1_standings[4] += 1
            elif replay_score[1] > replay_score[0]:
                team_2_standings[4] += 1
            else:
                third_place = third_place_playoff[random.randrange(0, 2)]
                if third_place == team_1:
                    team_1_standings[4] += 1
                else:
                    team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 2
        team_2_standings[4] += 2
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            replay_score = match_result(team_1_elo, team_2_elo)
            if replay_score[0] > replay_score[1]:
                team_1_standings[4] += 1
            elif replay_score[1] > replay_score[0]:
                team_2_standings[4] += 1
            else:
                champion = finalists[random.randrange(0, 2)]
                if champion == team_1:
                    team_1_standings[4] += 1
                else:
                    team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1950(self):
        is_starting = self.is_starting
        year = self.year
        groups = [['Brazil', 'Mexico', 'Serbia', 'Switzerland'], ['England', 'Spain', 'Chile', 'United States'],
                  ['Sweden', 'Italy', 'Paraguay'], ['Uruguay', 'Bolivia']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        final_group = []
        for group in groups:
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, 1950)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Determines if a replay is needed to tiebreak the group winner and adds the group winner to the final group
            first_place = group_standings[0]
            second_place = group_standings[1]
            if first_place[1] == second_place[1]:
                first_place_team_name = first_place[0]
                second_place_team_name = second_place[0]
                first_place_elo = group_elo_ratings[first_place_team_name]
                second_place_elo = group_elo_ratings[second_place_team_name]
                replay_score = match_result(first_place_elo, second_place_elo)
                if replay_score[0] > replay_score[1]:
                    final_group.append(first_place_team_name)
                elif replay_score[1] > replay_score[0]:
                    final_group.append(second_place_team_name)
                else:
                    group_winner = [first_place_team_name, second_place_team_name][random.randrange(0, 2)]
                    final_group.append(group_winner)
            else:
                final_group.append(first_place[0])
        # Final Group
        matches = []
        # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
        group_standings_dict = {}
        group_elo_ratings = {}
        # Creates matches to be played during the Group Stage
        for team_1_pos, team_1 in enumerate(final_group):
            for team_2_pos, team_2 in enumerate(final_group):
                if team_1_pos < team_2_pos:
                    matches.append([team_1, team_2])
            group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, 1950)})
            group_standings_dict.update({team_1: [0, 0, 0, 0]})
        # Simulates the Final Group Stage Matches
        final_group_ranking = []
        for match in matches:
            team_1 = match[0]
            team_2 = match[1]
            team_1_rating = group_elo_ratings[team_1]
            team_2_rating = group_elo_ratings[team_2]
            score = match_result(team_1_rating, team_2_rating)
            team_1_standings = group_standings_dict[team_1]
            team_2_standings = group_standings_dict[team_2]
            if score[0] > score[1]:
                team_1_standings[0] = team_1_standings[0] + 2
            elif score[0] == score[1]:
                team_1_standings[0] = team_1_standings[0] + 1
                team_2_standings[0] = team_2_standings[0] + 1
            else:
                team_2_standings[0] = team_2_standings[0] + 2
            team_1_standings[1] += score[0]
            team_2_standings[1] += score[1]
            team_1_standings[2] += score[1]
            team_2_standings[2] += score[0]
            team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
            team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
            group_standings_dict[team_1] = team_1_standings
            group_standings_dict[team_2] = team_2_standings
        # Updates the Full Tournament Standings and stores the Group Info into a List
        group_standings = []
        for team, data in group_standings_dict.items():
            team_data = [team]
            team_data.extend(data)
            group_standings.append(team_data)
            total_standings = full_tournament_standings[team]
            total_standings[0] += data[0]
            total_standings[1] += data[1]
            total_standings[2] += data[2]
            total_standings[3] += data[3]
            total_standings[4] += 1
            full_tournament_standings[team] = total_standings
        # Ranks the team in the Group
        group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
        # Determines if a replay is needed to tiebreak the group winner and adds the group winner to the final group
        first_place = group_standings[0]
        second_place = group_standings[1]
        third_place = group_standings[2]
        fourth_place = group_standings[3]
        if first_place[1] == second_place[1]:
            first_place_team_name = first_place[0]
            second_place_team_name = second_place[0]
            third_place_team_name = third_place[0]
            fourth_place_team_name = fourth_place[0]
            first_place_elo = group_elo_ratings[first_place_team_name]
            second_place_elo = group_elo_ratings[second_place_team_name]
            replay_score = match_result(first_place_elo, second_place_elo)
            if replay_score[0] > replay_score[1]:
                for team in group_standings:
                    final_group_ranking.append(team[0])
            elif replay_score[1] > replay_score[0]:
                final_group_ranking = [second_place_team_name, first_place_team_name, third_place_team_name,
                                       fourth_place_team_name]
            else:
                top_two_teams = [first_place_team_name, second_place_team_name]
                random.shuffle(top_two_teams)
                final_group_ranking = top_two_teams + [third_place_team_name, fourth_place_team_name]
        else:
            for team in group_standings:
                final_group_ranking.append(team[0])
        for rank, team in enumerate(final_group_ranking):
            team_standings = full_tournament_standings[team]
            team_standings[4] += 3 - rank
            full_tournament_standings[team] = team_standings
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1954(self):
        is_starting = self.is_starting
        year = self.year
        groups = [['Brazil', 'France', 'Mexico', 'Serbia'], ['Hungary', 'Turkey', 'Germany', 'South Korea'],
                  ['Uruguay', 'Austria', 'Czech Republic', 'Scotland'], ['Italy', 'England', 'Switzerland', 'Belgium']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        quarterfinalists = []
        for group in groups:
            seeded_teams = group[0:2]
            unseeded_teams = group[2:]
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                if team_1_pos < 2:
                    for team_2_pos, team_2 in enumerate(unseeded_teams):
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, 1954)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Determines if a replay is needed to tiebreak the group winner and adds the group winner to the final group
            first_place = group_standings[0]
            second_place = group_standings[1]
            third_place = group_standings[2]
            first_place_team_name = first_place[0]
            second_place_team_name = second_place[0]
            third_place_team_name = third_place[0]
            if second_place[1] == third_place[1]:
                second_place_elo = group_elo_ratings[second_place_team_name]
                third_place_elo = group_elo_ratings[third_place_team_name]
                replay_score = match_result(third_place_elo, second_place_elo)
                if replay_score[0] > replay_score[1]:
                    quarterfinalists.append([first_place_team_name, second_place_team_name])
                elif replay_score[1] > replay_score[0]:
                    quarterfinalists.append([first_place_team_name, third_place_team_name])
                else:
                    group_runner_up = [second_place_team_name, third_place_team_name][random.randrange(0, 2)]
                    quarterfinalists.append([first_place_team_name, group_runner_up])
            else:
                quarterfinalists.append([first_place_team_name, second_place_team_name])
        # shuffles the quarterfinalists for the draw
        for group in quarterfinalists:
            random.shuffle(group)
        qf_matchups = [[], [], [], []]
        for matchup_number, matchup in enumerate(qf_matchups):
            if matchup_number % 2 == 0:
                team_1 = quarterfinalists[matchup_number][0]
                team_2 = quarterfinalists[matchup_number + 1][0]
                qf_matchups[matchup_number] = [team_1, team_2]
            else:
                team_1 = quarterfinalists[matchup_number][1]
                team_2 = quarterfinalists[matchup_number - 1][1]
                qf_matchups[matchup_number] = [team_1, team_2]
        # Quarterfinal Stage
        semifinalists = [[], []]
        for matchup_number, matchup in enumerate(qf_matchups):
            sf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, 1954)
            team_2_elo = team_wc_rating(is_starting, team_2, 1954)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                semifinalists[sf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                semifinalists[sf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                replay_score = match_result(team_1_elo, team_2_elo)
                if replay_score[0] > replay_score[1]:
                    semifinalists[sf_match].append(team_1)
                elif replay_score[1] > replay_score[0]:
                    semifinalists[sf_match].append(team_2)
                else:
                    semifinalists[sf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # shuffles the semifinalists for the draw
        for group in semifinalists:
            random.shuffle(group)
        sf_matchups = [[], []]
        for matchup_number, matchup in enumerate(sf_matchups):
            if matchup_number % 2 == 0:
                team_1 = semifinalists[matchup_number][0]
                team_2 = semifinalists[matchup_number + 1][0]
                sf_matchups[matchup_number] = [team_1, team_2]
            else:
                team_1 = semifinalists[matchup_number][1]
                team_2 = semifinalists[matchup_number - 1][1]
                sf_matchups[matchup_number] = [team_1, team_2]
        # Semifinal Stage
        finalists = []
        third_place_playoff = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, 1954)
            team_2_elo = team_wc_rating(is_starting, team_2, 1954)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                finalists.append(team_1)
                third_place_playoff.append(team_2)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                finalists.append(team_2)
                third_place_playoff.append(team_1)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                replay_score = match_result(team_1_elo, team_2_elo)
                if replay_score[0] > replay_score[1]:
                    finalists.append(team_1)
                    third_place_playoff.append(team_2)
                elif replay_score[1] > replay_score[0]:
                    finalists.append(team_2)
                    third_place_playoff.append(team_1)
                else:
                    finalist = matchup[random.randrange(0, 2)]
                    finalists.append(finalist)
                    if team_1 == finalist:
                        third_place_playoff.append(team_2)
                    else:
                        third_place_playoff.append(team_1)
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, 1954)
        team_2_elo = team_wc_rating(is_starting, team_2, 1954)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            replay_score = match_result(team_1_elo, team_2_elo)
            if replay_score[0] > replay_score[1]:
                team_1_standings[4] += 1
            elif replay_score[1] > replay_score[0]:
                team_2_standings[4] += 1
            else:
                third_place = third_place_playoff[random.randrange(0, 2)]
                if third_place == team_1:
                    team_1_standings[4] += 1
                else:
                    team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, 1954)
        team_2_elo = team_wc_rating(is_starting, team_2, 1954)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 2
        team_2_standings[4] += 2
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            replay_score = match_result(team_1_elo, team_2_elo)
            if replay_score[0] > replay_score[1]:
                team_1_standings[4] += 1
            elif replay_score[1] > replay_score[0]:
                team_2_standings[4] += 1
            else:
                champion = finalists[random.randrange(0, 2)]
                if champion == team_1:
                    team_1_standings[4] += 1
                else:
                    team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1958_to_1970(self):
        is_starting = self.is_starting
        year = self.year
        if year == 1958:
            groups = [['Argentina', 'Germany', 'Northern Ireland', 'Czech Republic'],
                      ['France', 'Paraguay', 'Serbia', 'Scotland'], ['Sweden', 'Mexico', 'Hungary', 'Wales'],
                      ['Brazil', 'Austria', 'Russia', 'England']]
        elif year == 1962:
            groups = [['Uruguay', 'Colombia', 'Russia', 'Serbia'], ['Chile', 'Switzerland', 'Germany', 'Italy'],
                      ['Brazil', 'Mexico', 'Czech Republic', 'Spain'], ['Argentina', 'Bulgaria', 'Hungary', 'England']]
        elif year == 1966:
            groups = [['England', 'Uruguay', 'France', 'Mexico'], ['Germany', 'Switzerland', 'Argentina', 'Spain'],
                      ['Brazil', 'Bulgaria', 'Portugal', 'Hungary'], ['Russia', 'North Korea', 'Italy', 'Chile']]
        elif year == 1970:
            groups = [['Mexico', 'Russia', 'Belgium', 'El Salvador'], ['Uruguay', 'Israel', 'Italy', 'Sweden'],
                      ['Romania', 'England', 'Czech Republic', 'Brazil'], ['Peru', 'Bulgaria', 'Germany', 'Morocco']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        group_winners = []
        group_runner_ups = []
        for group in groups:
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD, GR],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, year)})
                group_standings_dict.update({team_1: [0, 0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                if team_1_standings[2] == 0:
                    team_1_standings[4] == 99
                else:
                    team_1_standings[4] = team_1_standings[1] / team_1_standings[2]
                if team_2_standings[2] == 0:
                    team_2_standings[4] == 99
                else:
                    team_2_standings[4] = team_2_standings[1] / team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data[0:4]
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            # 1970 Ranked Teams even on points by Goal Difference compared to Goal Ratio from 1958 to 1966
            if year == 1970:
                group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            else:
                group_standings = sorted(group_standings, key=lambda data: (data[1], data[5], data[4], data[2])
                                         , reverse=True)
            # Determines if a replay is needed to tiebreak the group winner and adds the group winner to the final group
            first_place = group_standings[0]
            second_place = group_standings[1]
            third_place = group_standings[2]
            first_place_team_name = first_place[0]
            second_place_team_name = second_place[0]
            third_place_team_name = third_place[0]
            group_winners.append(first_place_team_name)
            if year == 1958:
                if second_place[1] == third_place[1]:
                    second_place_elo = group_elo_ratings[second_place_team_name]
                    third_place_elo = group_elo_ratings[third_place_team_name]
                    replay_score = match_result(third_place_elo, second_place_elo)
                    if replay_score[0] < replay_score[1]:
                        group_runner_ups.append(third_place_team_name)
                    else:
                        group_runner_ups.append(second_place_team_name)
                else:
                    group_runner_ups.append(second_place_team_name)
            else:
                group_runner_ups.append(second_place_team_name)
        # Quarterfinals
        qf_matchups = [[0, 1], [2, 3], [1, 0], [3, 2]]
        for matchup_number, matchup in enumerate(qf_matchups):
            team_1 = group_winners[matchup[0]]
            team_2 = group_runner_ups[matchup[1]]
            qf_matchups[matchup_number] = [team_1, team_2]
        sf_matchups = [[], []]
        for matchup_number, matchup in enumerate(qf_matchups):
            sf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                sf_matchups[sf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                sf_matchups[sf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                sf_matchups[sf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Semifinal Stage
        finalists = []
        third_place_playoff = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                finalists.append(team_1)
                third_place_playoff.append(team_2)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                finalists.append(team_2)
                third_place_playoff.append(team_1)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                finalist = matchup[random.randrange(0, 2)]
                finalists.append(finalist)
                if team_1 == finalist:
                    third_place_playoff.append(team_2)
                else:
                    third_place_playoff.append(team_1)
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            third_place = third_place_playoff[random.randrange(0, 2)]
            if third_place == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 2
        team_2_standings[4] += 2
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            replay_score = match_result(team_1_elo, team_2_elo)
            if replay_score[0] > replay_score[1]:
                team_1_standings[4] += 1
            elif replay_score[1] > replay_score[0]:
                team_2_standings[4] += 1
            else:
                champion = finalists[random.randrange(0, 2)]
                if champion == team_1:
                    team_1_standings[4] += 1
                else:
                    team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1974_and_1978(self):
        is_starting = self.is_starting
        year = self.year
        if year == 1974:
            groups = [['Germany', 'Chile', 'East Germany', 'Australia'], ['Brazil', 'Serbia', 'DR Congo', 'Scotland'],
                      ['Uruguay', 'Netherlands', 'Sweden', 'Bulgaria'], ['Italy', 'Haiti', 'Poland', 'Argentina']]
        elif year == 1978:
            groups = [['Argentina', 'Hungary', 'Italy', 'France'], ['Germany', 'Poland', 'Tunisia', 'Mexico'],
                      ['Brazil', 'Sweden', 'Austria', 'Spain'], ['Netherlands', 'Iran', 'Peru', 'Scotland']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        second_round_groups = [[], []]
        for group_number, group in enumerate(groups):
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, year)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Teams advancing to the Next Round
            if group_number % 2 == 0:
                second_round_groups[0].append(group_standings[0][0])
                second_round_groups[1].append(group_standings[1][0])
            else:
                second_round_groups[0].append(group_standings[1][0])
                second_round_groups[1].append(group_standings[0][0])
        # Second Round of Group Stage
        third_place_playoff = []
        finalists = []
        for group in second_round_groups:
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, year)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0] += data[0]
                total_standings[1] += data[1]
                total_standings[2] += data[2]
                total_standings[3] += data[3]
                total_standings[4] += 1
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Teams advancing to the Next Round
            third_place_playoff.append(group_standings[1][0])
            finalists.append(group_standings[0][0])
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 1
        team_2_standings[4] += 1
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            third_place = third_place_playoff[random.randrange(0, 2)]
            if third_place == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 3
        team_2_standings[4] += 3
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            champion = finalists[random.randrange(0, 2)]
            if champion == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1982(self):
        is_starting = self.is_starting
        year = self.year
        groups = [['Italy', 'Poland', 'Peru', 'Cameroon'], ['Germany', 'Algeria', 'Chile', 'Austria'],
                  ['Argentina', 'Belgium', 'Hungary', 'El Salvador'], ['England', 'France', 'Czech Republic', 'Kuwait'],
                  ['Spain', 'Honduras', 'Serbia', 'Northern Ireland'], ['Brazil', 'Russia', 'Scotland', 'New Zealand']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        second_round_groups = [[], [], [], []]
        for group_number, group in enumerate(groups):
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, 1982)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Teams advancing to the Next Round
            if group_number % 2 == 0:
                if group_number < 4:
                    second_round_groups[0].append(group_standings[0][0])
                    second_round_groups[2].append(group_standings[1][0])
                else:
                    second_round_groups[3].append(group_standings[0][0])
                    second_round_groups[1].append(group_standings[1][0])
            else:
                if group_number < 5:
                    second_round_groups[1].append(group_standings[0][0])
                    second_round_groups[3].append(group_standings[1][0])
                else:
                    second_round_groups[2].append(group_standings[0][0])
                    second_round_groups[0].append(group_standings[1][0])
        # Second Round of Group Stage
        sf_matchups = [[], []]
        for group_number, group in enumerate(second_round_groups):
            sf_matchup = group_number % 2
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, 1982)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 2
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 2
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0] += data[0]
                total_standings[1] += data[1]
                total_standings[2] += data[2]
                total_standings[3] += data[3]
                total_standings[4] += 1
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Teams advancing to the Next Round
            sf_matchups[sf_matchup].append(group_standings[0][0])
        # Semifinal Stage
        finalists = []
        third_place_playoff = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, 1982)
            team_2_elo = team_wc_rating(is_starting, team_2, 1982)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 2
                finalists.append(team_1)
                third_place_playoff.append(team_2)
            elif score[1] > score[0]:
                team_2_standings[0] += 2
                finalists.append(team_2)
                third_place_playoff.append(team_1)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                finalist = matchup[random.randrange(0, 2)]
                finalists.append(finalist)
                if team_1 == finalist:
                    third_place_playoff.append(team_2)
                else:
                    third_place_playoff.append(team_1)
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, 1982)
        team_2_elo = team_wc_rating(is_starting, team_2, 1982)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            third_place = third_place_playoff[random.randrange(0, 2)]
            if third_place == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, 1982)
        team_2_elo = team_wc_rating(is_starting, team_2, 1982)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 2
        team_2_standings[4] += 2
        if score[0] > score[1]:
            team_1_standings[0] += 2
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 2
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            champion = finalists[random.randrange(0, 2)]
            if champion == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1986_to_1994(self):
        is_starting = self.is_starting
        year = self.year
        # points for a win
        win_pts = 2
        if year == 1986:
            groups = [['Italy', 'Argentina', 'Bulgaria', 'South Korea'], ['Mexico', 'Belgium', 'Paraguay', 'Iraq'],
                      ['France', 'Canada', 'Russia', 'Hungary'], ['Brazil', 'Spain', 'Algeria', 'Northern Ireland'],
                      ['Germany', 'Uruguay', 'Scotland', 'Denmark'], ['Poland', 'Morocco', 'Portugal', 'England']]
        elif year == 1990:
            groups = [['Italy', 'Austria', 'United States', 'Czech Republic'],
                      ['Argentina', 'Cameroon', 'Russia', 'Romania'], ['Brazil', 'Sweden', 'Costa Rica', 'Scotland'],
                      ['Germany', 'Serbia', 'UAE', 'Colombia'], ['Belgium', 'South Korea', 'Uruguay', 'Spain'],
                      ['England', 'Ireland', 'Netherlands', 'Egypt']]
        elif year == 1994:
            groups = [['United States', 'Switzerland', 'Colombia', 'Romania'],
                      ['Brazil', 'Russia', 'Cameroon', 'Sweden'],
                      ['Germany', 'Bolivia', 'Spain', 'South Korea'], ['Argentina', 'Greece', 'Nigeria', 'Bulgaria'],
                      ['Italy', 'Ireland', 'Norway', 'Mexico'], ['Belgium', 'Morocco', 'Netherlands', 'Saudi Arabia']]
            win_pts = 3
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        group_winners = []
        group_runners_up = []
        third_placed_teams = []
        for group_number, group in enumerate(groups):
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, year)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + win_pts
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + win_pts
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Teams advancing to the Next Round
            group_winners.append(group_standings[0][0])
            group_runners_up.append(group_standings[1][0])
            third_placed_teams.append([group_standings[2][0], group_number])
        # ranking 3rd placed teams, advancing the top 4, and setting Round of 16 Matchups
        third_placed_teams_standings = []
        for team in third_placed_teams:
            team_data = [team]
            team_data.extend(full_tournament_standings[team[0]])
            third_placed_teams_standings.append(team_data)
        third_placed_teams_standings = sorted(third_placed_teams_standings,
                                              key=lambda data: (data[1], data[4], data[2]), reverse=True)
        third_place_advancing_teams = third_placed_teams_standings[0:4]
        third_place_advancing_teams = sorted(third_place_advancing_teams, key=lambda data: data[0][1])
        third_place_groups_advancing = []
        for team in third_place_advancing_teams:
            third_place_groups_advancing.append(team[0][1])
        sequences = [[2, 3, 0, 1], [2, 0, 1, 4], [2, 0, 1, 5], [3, 0, 1, 4], [3, 0, 1, 5], [4, 0, 1, 5], [2, 3, 0, 4],
                     [2, 3, 0, 5], [2, 0, 5, 4], [3, 0, 5, 4], [2, 3, 1, 4], [2, 3, 1, 5], [4, 2, 1, 5], [4, 3, 1, 5],
                     [2, 3, 5, 4]]
        sequence_found = False
        for sequence in sequences:
            for group_of_team in third_place_groups_advancing:
                if group_of_team not in sequence:
                    sequence_found = False
                    break
                else:
                    sequence_found = True
            if sequence_found:
                third_place_sequence = sequence
                break
        if year == 1986:
            r16_matchups = [[group_winners[0], third_placed_teams[third_place_sequence[0]][0]],
                            [group_runners_up[1], group_runners_up[5]], [group_winners[4], group_runners_up[3]],
                            [group_winners[2], third_placed_teams[third_place_sequence[2]][0]],
                            [group_winners[3], third_placed_teams[third_place_sequence[3]][0]],
                            [group_runners_up[0], group_runners_up[2]],
                            [group_winners[5], group_runners_up[4]],
                            [group_winners[1], third_placed_teams[third_place_sequence[1]][0]]]
        elif year == 1990:
            r16_matchups = [[group_winners[2], third_placed_teams[third_place_sequence[2]][0]],
                            [group_winners[4], group_runners_up[3]], [group_runners_up[1], group_runners_up[5]],
                            [group_winners[0], third_placed_teams[third_place_sequence[0]][0]],
                            [group_runners_up[0], group_runners_up[2]],
                            [group_winners[3], third_placed_teams[third_place_sequence[3]][0]],
                            [group_winners[1], third_placed_teams[third_place_sequence[1]][0]],
                            [group_winners[5], group_runners_up[4]]]
        elif year == 1994:
            r16_matchups = [[group_winners[0], third_placed_teams[third_place_sequence[0]][0]],
                            [group_runners_up[1], group_runners_up[5]], [group_winners[5], group_runners_up[4]],
                            [group_winners[1], third_placed_teams[third_place_sequence[1]][0]],
                            [group_winners[4], group_runners_up[3]],
                            [group_winners[2], third_placed_teams[third_place_sequence[2]][0]],
                            [group_winners[3], third_placed_teams[third_place_sequence[3]][0]],
                            [group_runners_up[0], group_runners_up[2]]]
        # Round of 16
        qf_matchups = [[], [], [], []]
        for matchup_number, matchup in enumerate(r16_matchups):
            qf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += win_pts
                qf_matchups[qf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += win_pts
                qf_matchups[qf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                qf_matchups[qf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Quarterfinals
        sf_matchups = [[], []]
        for matchup_number, matchup in enumerate(qf_matchups):
            sf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += win_pts
                sf_matchups[sf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += win_pts
                sf_matchups[sf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                sf_matchups[sf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Semifinal Stage
        finalists = []
        third_place_playoff = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += win_pts
                finalists.append(team_1)
                third_place_playoff.append(team_2)
            elif score[1] > score[0]:
                team_2_standings[0] += win_pts
                finalists.append(team_2)
                third_place_playoff.append(team_1)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                finalist = matchup[random.randrange(0, 2)]
                finalists.append(finalist)
                if team_1 == finalist:
                    third_place_playoff.append(team_2)
                else:
                    third_place_playoff.append(team_1)
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        if score[0] > score[1]:
            team_1_standings[0] += win_pts
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += win_pts
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            third_place = third_place_playoff[random.randrange(0, 2)]
            if third_place == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 2
        team_2_standings[4] += 2
        if score[0] > score[1]:
            team_1_standings[0] += win_pts
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += win_pts
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            champion = finalists[random.randrange(0, 2)]
            if champion == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings

    def simulation_1998_onwards(self):
        is_starting = self.is_starting
        year = self.year
        if year == 1998:
            groups = [['Brazil', 'Scotland', 'Morocco', 'Norway'], ['Italy', 'Chile', 'Cameroon', 'Austria'],
                      ['France', 'South Africa', 'Saudi Arabia', 'Denmark'],
                      ['Spain', 'Nigeria', 'Paraguay', 'Bulgaria'],
                      ['Netherlands', 'Belgium', 'South Korea', 'Mexico'],
                      ['Germany', 'United States', 'Serbia', 'Iran'],
                      ['Romania', 'Colombia', 'England', 'Tunisia'], ['Argentina', 'Japan', 'Jamaica', 'Croatia']]
        elif year == 2002:
            groups = [['France', 'Senegal', 'Uruguay', 'Denmark'], ['Spain', 'Slovenia', 'Paraguay', 'South Africa'],
                      ['Brazil', 'Turkey', 'China', 'Costa Rica'],
                      ['South Korea', 'Poland', 'United States', 'Portugal'],
                      ['Germany', 'Saudi Arabia', 'Ireland', 'Cameroon'], ['Argentina', 'Nigeria', 'England', 'Sweden'],
                      ['Italy', 'Ecuador', 'Croatia', 'Mexico'], ['Japan', 'Belgium', 'Russia', 'Tunisia']]
        elif year == 2006:
            groups = [['Germany', 'Costa Rica', 'Poland', 'Ecuador'],
                      ['England', 'Paraguay', 'Trinidad and Tobago', 'Sweden'],
                      ['Argentina', 'Netherlands', 'Ivory Coast', 'Serbia'],
                      ['Mexico', 'Iran', 'Angola', 'Portugal'], ['Italy', 'Ghana', 'Czech Republic', 'United States'],
                      ['Brazil', 'Croatia', 'Australia', 'Japan'], ['France', 'Switzerland', 'South Korea', 'Togo'],
                      ['Spain', 'Ukraine', 'Tunisia', 'Saudi Arabia']]
        elif year == 2010:
            groups = [['South Africa', 'Mexico', 'Uruguay', 'France'],
                      ['Argentina', 'Nigeria', 'South Korea', 'Greece'],
                      ['England', 'United States', 'Algeria', 'Slovenia'], ['Germany', 'Australia', 'Serbia', 'Ghana'],
                      ['Netherlands', 'Denmark', 'Japan', 'Cameroon'], ['Italy', 'Paraguay', 'New Zealand', 'Slovakia'],
                      ['Brazil', 'North Korea', 'Ivory Coast', 'Portugal'],
                      ['Spain', 'Switzerland', 'Honduras', 'Chile']]
        elif year == 2014:
            groups = [['Brazil', 'Croatia', 'Mexico', 'Cameroon'], ['Spain', 'Netherlands', 'Chile', 'Australia'],
                      ['Colombia', 'Greece', 'Ivory Coast', 'Japan'], ['Uruguay', 'Costa Rica', 'England', 'Italy'],
                      ['Switzerland', 'Ecuador', 'France', 'Honduras'],
                      ['Argentina', 'Bosnia and Herzegovina', 'Iran', 'Nigeria'],
                      ['Germany', 'Portugal', 'Ghana', 'United States'],
                      ['Belgium', 'Algeria', 'Russia', 'South Korea']]
        elif year == 2018:
            groups = [['Russia', 'Saudi Arabia', 'Egypt', 'Uruguay'], ['Portugal', 'Spain', 'Morocco', 'Iran'],
                      ['France', 'Australia', 'Peru', 'Denmark'], ['Argentina', 'Iceland', 'Croatia', 'Nigeria'],
                      ['Brazil', 'Switzerland', 'Costa Rica', 'Serbia'], ['Germany', 'Mexico', 'Sweden', 'South Korea'],
                      ['Belgium', 'Panama', 'Tunisia', 'England'], ['Colombia', 'Japan', 'Poland', 'Senegal']]
        elif year == 2022:
            groups = [['Qatar', 'Ecuador', 'Senegal', 'Netherlands'], ['England', 'Iran', 'United States', 'Wales'],
                      ['Argentina', 'Saudi Arabia', 'Mexico', 'Poland'], ['France', 'Australia', 'Denmark', 'Tunisia'],
                      ['Spain', 'Costa Rica', 'Germany', 'Japan'], ['Belgium', 'Canada', 'Morocco', 'Croatia'],
                      ['Brazil', 'Switzerland', 'Cameroon', 'Serbia'], ['Portugal', 'Ghana', 'Uruguay', 'South Korea']]
        # full_tournament_standings should be in the format of {Team: [Points, GF, GA, GD, Round of Exit]}
        full_tournament_standings = {}
        # Group Stage
        group_winners = []
        group_runner_ups = []
        for group_number, group in enumerate(groups):
            matches = []
            # group_standings should be in the format of {Team: [Points, GF, GA, GD],...]
            group_standings_dict = {}
            group_elo_ratings = {}
            # Creates matches to be played during the Group Stage
            for team_1_pos, team_1 in enumerate(group):
                for team_2_pos, team_2 in enumerate(group):
                    if team_1_pos < team_2_pos:
                        matches.append([team_1, team_2])
                group_elo_ratings.update({team_1: team_wc_rating(is_starting, team_1, year)})
                group_standings_dict.update({team_1: [0, 0, 0, 0]})
                full_tournament_standings.update({team_1: [0, 0, 0, 0, 0]})
            # Simulates the Group Stage Matches
            for match in matches:
                team_1 = match[0]
                team_2 = match[1]
                team_1_rating = group_elo_ratings[team_1]
                team_2_rating = group_elo_ratings[team_2]
                score = match_result(team_1_rating, team_2_rating)
                team_1_standings = group_standings_dict[team_1]
                team_2_standings = group_standings_dict[team_2]
                if score[0] > score[1]:
                    team_1_standings[0] = team_1_standings[0] + 3
                elif score[0] == score[1]:
                    team_1_standings[0] = team_1_standings[0] + 1
                    team_2_standings[0] = team_2_standings[0] + 1
                else:
                    team_2_standings[0] = team_2_standings[0] + 3
                team_1_standings[1] += score[0]
                team_2_standings[1] += score[1]
                team_1_standings[2] += score[1]
                team_2_standings[2] += score[0]
                team_1_standings[3] = team_1_standings[1] - team_1_standings[2]
                team_2_standings[3] = team_2_standings[1] - team_2_standings[2]
                group_standings_dict[team_1] = team_1_standings
                group_standings_dict[team_2] = team_2_standings
            # Updates the Full Tournament Standings and stores the Group Info into a List
            group_standings = []
            for team, data in group_standings_dict.items():
                team_data = [team]
                team_data.extend(data)
                group_standings.append(team_data)
                total_standings = full_tournament_standings[team]
                total_standings[0:4] = data
                full_tournament_standings[team] = total_standings
            # Ranks the team in the Group
            group_standings = sorted(group_standings, key=lambda data: (data[1], data[4], data[2]), reverse=True)
            # Adds the Teams advancing to the Next Round
            group_winners.append(group_standings[0][0])
            group_runner_ups.append(group_standings[1][0])
        # Sets the Knockout Stage
        if year == 1998:
            r16_matchups = [[0, 1], [3, 2], [4, 5], [7, 6], [1, 0], [2, 3], [5, 4], [6, 7]]
        elif year == 2002:
            r16_matchups = [[4, 1], [6, 3], [1, 4], [3, 6], [0, 5], [2, 7], [5, 0], [7, 2]]
        else:
            r16_matchups = [[0, 1], [2, 3], [4, 5], [6, 7], [1, 0], [3, 2], [5, 4], [7, 6]]
        for matchup_number, matchup in enumerate(r16_matchups):
            team_1 = group_winners[matchup[0]]
            team_2 = group_runner_ups[matchup[1]]
            r16_matchups[matchup_number] = [team_1, team_2]
        # Round of 16
        qf_matchups = [[], [], [], []]
        for matchup_number, matchup in enumerate(r16_matchups):
            qf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 3
                qf_matchups[qf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 3
                qf_matchups[qf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                qf_matchups[qf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Quarterfinals
        sf_matchups = [[], []]
        for matchup_number, matchup in enumerate(qf_matchups):
            sf_match = matchup_number // 2
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 3
                sf_matchups[sf_match].append(team_1)
            elif score[1] > score[0]:
                team_2_standings[0] += 3
                sf_matchups[sf_match].append(team_2)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                sf_matchups[sf_match].append(matchup[random.randrange(0, 2)])
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Semifinal Stage
        finalists = []
        third_place_playoff = []
        for matchup in sf_matchups:
            team_1 = matchup[0]
            team_2 = matchup[1]
            team_1_elo = team_wc_rating(is_starting, team_1, year)
            team_2_elo = team_wc_rating(is_starting, team_2, year)
            score = match_result(team_1_elo, team_2_elo)
            team_1_standings = full_tournament_standings[team_1]
            team_2_standings = full_tournament_standings[team_2]
            team_1_standings[2] += score[0]
            team_1_standings[3] += score[1]
            team_2_standings[2] += score[1]
            team_2_standings[3] += score[0]
            team_1_standings[1] += score[0] - score[1]
            team_2_standings[1] += score[1] - score[0]
            team_1_standings[4] += 1
            team_2_standings[4] += 1
            if score[0] > score[1]:
                team_1_standings[0] += 3
                finalists.append(team_1)
                third_place_playoff.append(team_2)
            elif score[1] > score[0]:
                team_2_standings[0] += 3
                finalists.append(team_2)
                third_place_playoff.append(team_1)
            else:
                team_1_standings[0] += 1
                team_2_standings[0] += 1
                finalist = matchup[random.randrange(0, 2)]
                finalists.append(finalist)
                if team_1 == finalist:
                    third_place_playoff.append(team_2)
                else:
                    third_place_playoff.append(team_1)
            full_tournament_standings.update({team_1: team_1_standings})
            full_tournament_standings.update({team_2: team_2_standings})
        # Third Place Match
        team_1 = third_place_playoff[0]
        team_2 = third_place_playoff[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        if score[0] > score[1]:
            team_1_standings[0] += 3
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 3
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            third_place = third_place_playoff[random.randrange(0, 2)]
            if third_place == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Final
        team_1 = finalists[0]
        team_2 = finalists[1]
        team_1_elo = team_wc_rating(is_starting, team_1, year)
        team_2_elo = team_wc_rating(is_starting, team_2, year)
        score = match_result(team_1_elo, team_2_elo)
        team_1_standings = full_tournament_standings[team_1]
        team_2_standings = full_tournament_standings[team_2]
        team_1_standings[2] += score[0]
        team_1_standings[3] += score[1]
        team_2_standings[2] += score[1]
        team_2_standings[3] += score[0]
        team_1_standings[1] += score[0] - score[1]
        team_2_standings[1] += score[1] - score[0]
        team_1_standings[4] += 2
        team_2_standings[4] += 2
        if score[0] > score[1]:
            team_1_standings[0] += 3
            team_1_standings[4] += 1
        elif score[1] > score[0]:
            team_2_standings[0] += 3
            team_2_standings[4] += 1
        else:
            team_1_standings[0] += 1
            team_2_standings[0] += 1
            champion = finalists[random.randrange(0, 2)]
            if champion == team_1:
                team_1_standings[4] += 1
            else:
                team_2_standings[4] += 1
        full_tournament_standings.update({team_1: team_1_standings})
        full_tournament_standings.update({team_2: team_2_standings})
        # Full Tournament Standings into a List used to determine the Final Ranked Standings
        final_tournament_standings = []
        for team, data in full_tournament_standings.items():
            team_data = [team]
            team_data.extend(data)
            final_tournament_standings.append(team_data)
        final_tournament_standings = sorted(final_tournament_standings,
                                            key=lambda data: (data[5], data[1], data[4], data[2]), reverse=True)
        # Final Tournament Standings are in the form of [[Team, Points, GF, GA, GD, Rounds advanced], ...]
        return final_tournament_standings
    def final_standings(self):
        year = self.year
        if year == 1930:
            results = self.simulation_1930()
        elif year == 1934 or year == 1938:
            results = self.simulation_1934_and_1938()
        elif year == 1950:
            results = self.simulation_1950()
        elif year == 1954:
            results = self.simulation_1954()
        elif 1958 <= year <= 1970:
            results = self.simulation_1958_to_1970()
        elif year == 1974 or year == 1978:
            results = self.simulation_1974_and_1978()
        elif year == 1982:
            results = self.simulation_1982()
        elif 1986 <= year <= 1994:
            results = self.simulation_1986_to_1994()
        elif year >= 1998:
            results = self.simulation_1998_onwards()
        return results