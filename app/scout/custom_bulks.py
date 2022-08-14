"""
Custom bulk functions.

Custom bulk get_or_create for Team model.
Custom bulk update_or_creat for Game model.

"""

from django.template.defaultfilters import slugify

from arena.models import Game, Team


def team_bulk_get_or_create(teams: dict, batch_size=100) -> dict:
    # 1. Get all existing teams (existing_teams) and put them into 'existing' dictionary.
    # 2. Collect all new teams (not_existing).
    # 3. Bulk create all new teams.
    # 4. Return dictionary {team_api_id: team_object}.

    existing_teams = Team.objects.filter(api_team_id__in=teams.keys())
    existing = {}

    for team in existing_teams:
        existing[team.api_team_id] = team
        teams.pop(team.api_team_id)

    not_existing = {}
    
    for api_id, team in teams.items():
        not_existing[api_id] = Team(
            api_team_id=team.api_team_id,
            name=team.name,
            short_name=team.name,
            slug=slugify('-'.join([str(team.api_team_id), team.name])),
        )

    Team.objects.bulk_create(not_existing.values(), batch_size)

    objs = {**existing, **not_existing}

    return objs


def game_bulk_update_or_create(games: dict, batch_size=100) -> None:
    # 1. Get all existing games (existing_games).
    # 2. Check if there is a new data for existing games (changed_games).
    # 3. Update existing games and create new games.

    fields = ['game_date', 'venue', 'city', 'referee', 'status', 'tournament_id',
    'season', 'round', 'home_team_id', 'away_team_id', 'home_goals_ht', 'away_goals_ht',
    'home_goals_ft', 'away_goals_ft','home_goals_et','away_goals_et', 'home_goals_pen',
    'away_goals_pen', 'pub_date', 'slug']

    existing_games = Game.objects.filter(api_game_id__in=games.keys())
    changed_games = []

    for game in existing_games:
        current_state = game.__dict__
        new_state = games.pop(game.api_game_id).__dict__
        changed = False
        for f in fields:
            if f == 'pub_date' and current_state['preview'] == None:
                current_state[f] = new_state[f]
                changed = True
            elif f != 'pub_date' and current_state[f] != new_state[f]:
                current_state[f] = new_state[f]
                changed = True
        if changed:
            changed_games.append(game)

    Game.objects.bulk_update(changed_games, fields, batch_size)
    Game.objects.bulk_create(games.values(), batch_size)
