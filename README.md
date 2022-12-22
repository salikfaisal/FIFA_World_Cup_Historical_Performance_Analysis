# FIFA_World_Cup_Historical_Performance_Analysis
This project simulated every World Cup 10,000 times using [Elo Ratings](http://www.eloratings.net/).

You can read the key findings and analysis in my article on [Medium](https://medium.com/@salikfaisal/analyzing-world-cup-history-with-elo-ratings-c83a9cf6c282).

[Team Data For Each Tournament](https://github.com/salikfaisal/FIFA_World_Cup_Historical_Performance_Analysis/blob/main/Historical_World_Cup_Teams.csv)<br>
[All Time Team Data](https://github.com/salikfaisal/FIFA_World_Cup_Historical_Performance_Analysis/blob/main/Overall_World_Cup_Team_Data.csv)

Varaiable | Description
--- | --- 
`Elo Rating` | Rating given to each team both before (Starting) and after (Final) the tournament.
`Prize Money (Millions of USD)` | Prize Money is utlized as a measure of World Cup Success. The allocations are based on the [2022 Distribution](https://www.fifa.com/tournaments/mens/worldcup/qatar2022/news/fifa-president-welcomes-participants-to-team-seminar).
`Expected World Cups` | This number represents the average number of World Cups won based on on Final Elo Ratings.
`Win A World Cup` | This number represents the probability that a country would have won at least one World Cup based on simulation results from Final Elo Ratings.
`Adjusted Win World Cup` | (The probability returned from the simulations) * (Number of Teams in Tournament) / 32. This is done so that the high probabilities in World Cups with less teams can be comparable to World Cups with more teams. The teams in the tournament number reflect the path to winning the tournament if every game had 50/50 odds. Numbers may vary among teams in the same World Cup (when the number of teams in each group is not equal).
`Tournament Performance Rating (TPR)` | A number on a scale from 0 to 1 indicating how well the team performed compared to what Elo ratings would suggest. This is based on adjusted 32-team probabilities. The number is calculated by subtracting the sum of the cumulative proability of achieving the final place from 1.
