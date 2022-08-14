from django.contrib import admin

from arena.models import Game, Team, Tournament


@admin.register(Tournament)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        'api_tour_id',
        'pseudonym',
        'name',
        'country',
        'base_rating',
        'av_defence',
        'av_attack',
        'av_goals_number',
        'is_championship',
        'is_running',
        )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'api_team_id',
        'short_name',
        'league',
        'defence',
        'attack',
        'coach',
        'rating_updated',
        )
    list_filter = ('league',)
    search_fields = ('name', 'short_name', 'coach')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'api_game_id',
        'season',
        'game_date',
        'country',
        'tournament',
        'home_team',
        'away_team',
        'home_goals_ft',
        'away_goals_ft',
        'pub_date',
        )
    list_filter = ('season', 'tournament')
    search_fields = ('tournament__name', 'home_team__name', 'away_team__name')

    def country(self, obj):
        return obj.tournament.country
