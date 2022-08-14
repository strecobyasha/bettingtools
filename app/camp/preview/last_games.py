"""
Team last games.

Collect last games during preview generating.
There are three types of last games lists: recent
games from all tournaments, from current tournament
and versus teams with the same class as current opponent.

"""

from django.db.models import F, Q

from arena.models import Game, Team, Tournament
from camp.models import LastGameModel

GAMES_NUMBER = 10

def get_team_last_games(
        team: Team,
        tournament: Tournament = None,
        team_class: int = None,
        opponent_class: int = None
) -> dict:
    # Last games for the team.
    filter1 = {'status': 'Match Finished'}
    filter2 = Q(home_team=team)|Q(away_team=team)
    if team_class:
        filter2 = Q(
                home_team=team,
                home_team_class=team_class,
                away_team_class=opponent_class,
            ) | Q(
                away_team=team,
                home_team_class=opponent_class,
                away_team_class=team_class,
            )
    elif tournament:
        filter1 = {'status': 'Match Finished', 'tournament': tournament}

    team_last_games = Game.objects.filter(**filter1).filter(filter2).select_related(
        'home_team', 'away_team'
    ).annotate(
            home_team_short_name=F('home_team__short_name'),
            away_team_short_name=F('away_team__short_name')
        )[:GAMES_NUMBER]

    games_data = {
        'last_games': [],
        'team_total_stats': {},
        'opponents_total_stats': {},
    }

    for game in team_last_games:
        game_model = LastGameModel(**game.__dict__)
        games_data['last_games'].append(dict(game_model))
        home_team_stats = game_model.home_team_stats
        away_team_stats = game_model.away_team_stats

        if home_team_stats and away_team_stats:
            if team.short_name == game_model.home_team_short_name:
                games_data['team_total_stats'] = collects_stats(games_data['team_total_stats'], home_team_stats)
                games_data['opponents_total_stats'] = collects_stats(
                    games_data['opponents_total_stats'], away_team_stats
                )
            else:
                games_data['team_total_stats'] = collects_stats(games_data['team_total_stats'], away_team_stats)
                games_data['opponents_total_stats'] = collects_stats(
                    games_data['opponents_total_stats'], home_team_stats
                )

    games_data['team_total_stats'] = average_stats(games_data['team_total_stats'])
    games_data['opponents_total_stats'] = average_stats(games_data['opponents_total_stats'])

    return games_data


def collects_stats(current_stats: dict, stats_to_add: dict) -> dict:
    # Collect stats from every game.
    for k, v in stats_to_add.items():
        if v != '':
            if type(v) is str and '%' in v:
                v = int(v.replace('%', ''))
            if v is None or v == 'None':
                v = 0
            current_stats.setdefault(k, []).append(int(v))

    return current_stats


def average_stats(stats: dict) -> dict:
    # Calculate average stats.
    for k, v in stats.items():
        stats[k] = round(sum(v) / len(v), 1)

    return stats
