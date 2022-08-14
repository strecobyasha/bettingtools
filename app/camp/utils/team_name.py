"""
Get name option for the team.

"""

import random

from camp.models import TeamModel


def get_team_name(team: TeamModel) -> str:
    options = []
    if team.name_variations:
        options = team.name_variations
    if team.coach:
        options.extend([f'the {team.coach}\'s team', f'the team of {team.coach}'])
    if options:
        return random.choice(options)

    return team.short_name
