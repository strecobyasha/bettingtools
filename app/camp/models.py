"""
Model to validate data.

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class GameModel(BaseModel):
    game_date: datetime
    venue: str
    game_odds: dict
    game_outcome_odds: Optional[dict]
    game_total_odds: Optional[dict]
    home_team_class: int
    away_team_class: int

    def __init__(self, **data):
        super().__init__(**data)
        self.game_outcome_odds = self.game_odds.get('Match Winner')
        self.game_total_odds = self.game_odds.get('Goals Over/Under')


class TeamModel(BaseModel):
    api_team_id: int
    name: str
    short_name: str
    defence: float
    attack: float
    coach: Optional[str]
    name_variations: Optional[list]


class TourModel(BaseModel):
    name: str
    name_variations: Optional[dict]


def convert_datetime(dt: datetime) -> str:
    return dt.strftime('%d/%m/%Y')

class LastGameModel(BaseModel):
    game_date: datetime
    home_team_short_name: str
    away_team_short_name: str
    home_goals_ft: int
    away_goals_ft: int
    game_odds: Optional[dict]
    home_team_stats: Optional[dict]
    away_team_stats: Optional[dict]
    game_events: Optional[list[dict]]

    _convert_datetime = validator(
        'game_date',
        allow_reuse=True
    )(convert_datetime)

    @validator('game_odds')
    def cut_odds(cls, v):
        if v:
            return v.get('Match Winner')
        return None

