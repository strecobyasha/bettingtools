"""
Read and write data from the database.

"""

from datetime import datetime, timedelta

from django.db.models import QuerySet
from django.template.defaultfilters import slugify

from arena.models import Game, Team, Tournament
from scout.custom_bulks import (game_bulk_update_or_create,
                                team_bulk_get_or_create)
from scout.models import GameModel, TeamModel

# The range for which games details should be parsed.
DETAILS_DELTA_BOTTOM = 3
DETAILS_DELTA_TOP = 7
# Posting time in hours relative to game date.
PUB_DATE_NORM = 56
PUB_DATE_MIN = 2

class GameDetailsUpdater:

    def __init__(
            self,
            field_to_check: str,
            fields_to_update: list,
            status: str = 'Match Finished',
            related: str = None):
        now = datetime.now().astimezone()
        date_from = now - timedelta(days=DETAILS_DELTA_BOTTOM)
        date_to = now + timedelta(days=DETAILS_DELTA_TOP)
        self.filter_data = {
            'status': status,
            'game_date__gte': date_from,
            'game_date__lte': date_to,
        }
        if field_to_check:
            self.filter_data[field_to_check + '__isnull'] = True
        self.fields_to_update = fields_to_update
        self.related = related

    def get_games_from_db(self) -> QuerySet:
        # Get a list of games ids to parse from API.
        return Game.objects.filter(**self.filter_data).values_list(
            'api_game_id',
            flat=True,
        )

    def get_games_to_update(self, games_details: dict) -> QuerySet:
        # Get a list of games with parsed details data.
        if self.related:
            return Game.objects.filter(
                api_game_id__in=games_details.keys()
            ).select_related(self.related)

        return Game.objects.filter(api_game_id__in=games_details.keys())

    def update_games(self, games_to_update: QuerySet) -> None:
        # Update games details in the DB.
        Game.objects.bulk_update(
            games_to_update,
            self.fields_to_update,
            batch_size=100,
        )


class ScoresUpdater:

    def get_running_tours(self) -> dict:
        # List of tournaments that will be assigned for each game (to prevent multiple queries).
        return {tour.api_tour_id: tour for tour in Tournament.objects.filter(is_running=True)}

    def prepare_data(self, games: list, tours: dict) -> dict:
        # List of teams, participating in games, that will be assigned for each game.
        # teams = {team['id']: team['name'] for game in games for team in game['teams'].values()}
        teams = {
            team['id']: TeamModel(api_team_id=team['id'], name=team['name'])
            for game in games
            for team in game['teams'].values()
        }
        teams_objs = team_bulk_get_or_create(teams)

        data_to_load = {}

        for game in games:
            tour = tours.get(game['league']['id'])
            home_team = teams_objs.get(game['teams']['home']['id'])
            away_team = teams_objs.get(game['teams']['away']['id'])
            game_date = datetime.fromisoformat(game['fixture']['date'])

            normal_pub_date = (game_date - timedelta(hours=PUB_DATE_NORM)).astimezone()
            earliest_pub_date = (datetime.now() + timedelta(hours=PUB_DATE_MIN)).astimezone()
            pub_date = max(normal_pub_date, earliest_pub_date)
            if pub_date > game_date + timedelta(hours=4):
                pub_date = None
            slug = slugify('-'.join([game_date.strftime('%Y-%m-%d'), home_team.name, away_team.name]))

            validated_game_data = GameModel(
                api_game_id=game['fixture']['id'],
                game_date=game_date,
                venue=game['fixture']['venue']['name'],
                city=game['fixture']['venue']['city'],
                referee=game['fixture']['referee'],
                status=game['fixture']['status']['long'],
                season=game['league']['season'],
                round=game['league']['round'],
                home_goals_ht=game['score']['halftime']['home'],
                away_goals_ht=game['score']['halftime']['away'],
                home_goals_ft=game['score']['fulltime']['home'],
                away_goals_ft=game['score']['fulltime']['away'],
                home_goals_et=game['score']['extratime']['home'],
                away_goals_et=game['score']['extratime']['away'],
                home_goals_pen=game['score']['penalty']['home'],
                away_goals_pen=game['score']['penalty']['away'],
                pub_date=pub_date,
                slug=slug,
            )

            data_to_load[game['fixture']['id']] = Game(
                **validated_game_data.__dict__,
                home_team=home_team,
                away_team=away_team,
                tournament=tour,
            )

        return data_to_load

    def update_or_create_games(self, data_to_load: dict) -> None:
        # Update or create games in the DB.
        game_bulk_update_or_create(data_to_load)


class StandingsUpdater():

    def get_running_tours(self) -> dict:
        # List of tournaments that will be assigned for each game (to prevent multiple queries).
        return {tour.api_tour_id: tour for tour in Tournament.objects.filter(is_running=True)}

    def prepare_data(self, standings_data: iter, tours: dict) -> dict:
        teams_in_db = {
            team['api_team_id']: {'name': team['short_name'], 'slug': team['slug'], 'logo': team['logo']}
            for team in Team.objects.all().values('api_team_id', 'short_name', 'slug', 'logo')
        }

        for data in standings_data:
            tour_id = data['id']
            tour_standings = {}
            # List of standings: one element for ordinary championships (e.g. EPL),
            # several elements for tournaments such as UEFA Champions League.
            standings = data['standings']
            for group in standings:
                group_name = group[0]['group']
                teams = []
                for team in group:
                    team_data = {
                        'rank': team['rank'],
                        'rank_description': team['description'],
                        'api_team_id': team['team']['id'],
                        'team_name': teams_in_db.get(team['team']['id']) if teams_in_db.get(team['team']['id']) is
                                    not None else {'name': team['team']['name'], 'slug': None, 'logo': None},
                        'status': team['status'],
                        'stats_all': self.modify_stats(team['all'], team['points'], team['goalsDiff']),
                        'stats_home': self.modify_stats(team['home']),
                        'stats_away': self.modify_stats(team['away']),
                    }
                    teams.append(team_data)
                tour_standings[group_name] = teams
            tours[tour_id].standings = tour_standings

        return tours

    def rename_team(self, id):
        return Team.objects.get(api_team_id=id)

    def modify_stats(self, data: dict, points: int = None, goals_diff: int = None) -> dict:
        stats = {
            'played': data['played'],
            'win': data['win'],
            'draw': data['draw'],
            'lose': data['lose'],
            'goals_for': data['goals']['for'],
            'goals_against': data['goals']['against'],
        }
        if points:
            stats['points'] = points
            stats['goals_diff'] = goals_diff
        else:
            try:
                stats['points'] = data['win'] * 3 + data['draw']
            except TypeError:
                stats['points'] = 0
            try:
                stats['goals_diff'] = data['goals']['for'] - data['goals']['against']
            except TypeError:
                stats['goals_diff'] = 0

        return stats

    def update_tours(self, tours: dict) -> None:
        Tournament.objects.bulk_update(tours.values(), ['standings'])
