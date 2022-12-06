"""
Get games odds from the Api.

Make requests to the Api to get odds for the upcoming games
with empty 'game_odds' field in the DB.
"""

from datetime import datetime

from django.db.models import QuerySet

from scout.parsers import DetailsParser
from scout.updaters import GameDetailsUpdater
from scout.updates_managers import DetailsUpdatesManager


class OddsUpdater(GameDetailsUpdater):

    def update_details(self, games_to_update: QuerySet, games_odds: dict) -> None:
        # Prepare events data and update games in the DB.
        for game in games_to_update.iterator():
            api_odds = self.prepare_odds(games_odds[game.api_game_id])
            odds = self.combine_odds(game.game_odds, api_odds)
            if 'Match Winner' in odds:
                home_team_class, away_team_class = self.determine_team_class(odds['Match Winner'])
            else:
                home_team_class, away_team_class = 0, 0
            game.game_odds = odds
            game.home_team_class = home_team_class
            game.away_team_class = away_team_class

    def prepare_odds(self, data: list[dict]) -> dict:
        # Get odds from Api as the next structure:
        # bookie -> bet type (e.g. 'Match Winner') ->
        # bet value (e.g. 'Home') -> odds value (e.g. 2.20).
        # Then convert to the new structure:
        # bet type -> bet value -> [odds values].
        odds_collection = {}
        bookies = data[0]['bookmakers']
        for bookie in bookies:
            bets = bookie['bets']
            for bet in bets:
                name = bet['name']
                odds_collection.setdefault(name, {})
                values = bet['values']
                for value in values:
                    if 'odd' in value:
                        odds_collection[name].setdefault(
                            value['value'],
                            [],
                        ).append(value['odd'])
        return odds_collection

    def combine_odds(self, obj_odds: dict, odds_collection: dict) -> dict:
        # Add new odds to the lists of odds values.
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        if obj_odds is None:
            obj_odds = {'created': now, 'updated': now}
        for key, subkeys in odds_collection.items():
            for subkey, value in subkeys.items():
                obj_odds.setdefault(key, {}).setdefault(subkey, [1, 1])
                odds_list = obj_odds[key][subkey]
                # Average value of the odds for all bookies.
                av_odds = round(sum([float(item) for item in value]) / len(value), 2)
                if odds_list[0] == 1:
                    odds_list[0] = av_odds
                odds_list[1] = av_odds
        obj_odds['updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        return obj_odds

    def determine_team_class(self, odds: dict) -> tuple:
        breakpoints = (1.25, 1.6, 2, 2.4, 2.95, 3.7, 5.5, 12)
        home_win_odds = odds['Home'][-1]
        away_win_odds = odds['Away'][-1]
        home_team_class = 0
        away_team_class = 0
        while home_win_odds > breakpoints[home_team_class]:
            home_team_class += 1
            if home_team_class > len(breakpoints) - 1:
                break

        while away_win_odds > breakpoints[away_team_class]:
            away_team_class += 1
            if away_team_class > len(breakpoints) - 1:
                break

        return (home_team_class, away_team_class)


def updater() -> None:
    odds_updater = OddsUpdater(
        field_to_check='',
        fields_to_update=['game_odds','home_team_class', 'away_team_class'],
        status='Not Started',
    )
    odds_parser = DetailsParser(url_tail='odds')
    updates_manager = DetailsUpdatesManager(
        updater=odds_updater,
        parser=odds_parser,
    )
    updates_manager.start_updating()
