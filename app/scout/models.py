"""
Models to validate data from the API.

"""

from datetime import datetime
from typing import Union

from pydantic import BaseModel


class TeamModel(BaseModel):
    api_team_id: int
    name: str


class GameModel(BaseModel):
    api_game_id: int
    game_date: datetime
    venue: Union[str, None]
    city: Union[str, None]
    referee: Union[str, None]
    status: str
    season: int
    round: Union[str, None]
    home_goals_ht: Union[int, None]
    away_goals_ht: Union[int, None]
    home_goals_ft: Union[int, None]
    away_goals_ft: Union[int, None]
    home_goals_et: Union[int, None]
    away_goals_et: Union[int, None]
    home_goals_pen: Union[int, None]
    away_goals_pen: Union[int, None]
    pub_date: Union[datetime, None]
    slug: str
