import uuid

from datetime import datetime
from django.db import models
from django.db.models import F, Q, Sum, QuerySet
from django.db.models.fields.json import KeyTextTransform
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from camp.preview.last_games import average_stats, collects_stats


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Tournament(UUIDMixin):
    api_tour_id = models.IntegerField(unique=True)
    pseudonym = models.CharField(max_length=255)
    name = models.CharField(_('name'), max_length=255)
    country = models.CharField(_('country'), max_length=255)
    current_season = models.IntegerField()
    logo = models.ImageField(default='/tours_logos/default.png')
    name_variations = models.JSONField(blank=True, null=True)
    base_rating = models.IntegerField(default=0)
    av_defence = models.FloatField(default=0)
    av_attack = models.FloatField(default=0)
    av_goals_number = models.FloatField(default=1.25)
    standings = models.JSONField(blank=True, null=True)
    bookies_standings = models.JSONField(blank=True, null=True)
    predicted_standings = models.JSONField(blank=True, null=True)
    is_championship = models.BooleanField(default=True)
    is_running = models.BooleanField(default=True)
    slug = models.SlugField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.pseudonym

    class Meta:
        db_table = 'content\".\"tournament'
        ordering = ['pseudonym']


class Team(UUIDMixin):
    api_team_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(_('name'), max_length=255)
    short_name = models.CharField(_('short_name'), max_length=255)
    city = models.CharField(max_length=255, blank=True, null=True)
    stadium = models.CharField(max_length=255, blank=True, null=True)
    stadium_capacity = models.IntegerField(blank=True, null=True)
    league = models.ForeignKey(
        'Tournament',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    defence = models.FloatField(default=0)
    attack = models.FloatField(default=0)
    coach = models.CharField(max_length=255, blank=True)
    name_variations = models.JSONField(blank=True, null=True)
    logo = models.ImageField(default='/teams_logos/default.png')
    rating_updated = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.short_name

    def save(self, *args, **kwargs):
        self.slug = slugify('-'.join([str(self.api_team_id), self.name]))
        super().save(*args, **kwargs)

    def get_team_stats(obj, latest_games: QuerySet) -> dict:
        team_stats = {
            'team_total_stats': {},
            'opponents_total_stats': {},
        }
        for game in latest_games:
            if game.home_team_stats and game.away_team_stats:
                if obj == game.home_team:
                    team_stats['team_total_stats'] = collects_stats(
                        team_stats['team_total_stats'], game.home_team_stats
                    )
                    team_stats['opponents_total_stats'] = collects_stats(
                        team_stats['opponents_total_stats'], game.away_team_stats
                    )
                else:
                    team_stats['team_total_stats'] = collects_stats(
                        team_stats['team_total_stats'], game.away_team_stats
                    )
                    team_stats['opponents_total_stats'] = collects_stats(
                        team_stats['opponents_total_stats'], game.home_team_stats
                    )
        team_stats['team_total_stats'] = average_stats(team_stats['team_total_stats'])
        team_stats['opponents_total_stats'] = average_stats(team_stats['opponents_total_stats'])

        return team_stats

    class Meta:
        db_table = 'content\".\"team'
        ordering = ['short_name']


class GameManager(models.Manager):

    def get_next_games(self, now: datetime) -> QuerySet:
        return self.filter(
                status='Not Started',
                pub_date__lte=now
            ).annotate(
                outcome_odds=KeyTextTransform('Match Winner', 'game_odds')
            ).order_by('game_date')[:5].select_related('home_team', 'away_team')

    def get_main_games(self, now: datetime) -> QuerySet:
        return self.filter(
                status='Not Started',
                pub_date__lte=now,
            ).annotate(
                game_rating=Sum(
                    F('home_team_defence') + F('away_team_defence') + F('home_team_attack') + F('away_team_attack')
                ),
                outcome_odds=KeyTextTransform('Match Winner', 'game_odds')
            ).order_by(
                '-game_rating'
            )[:5].select_related('home_team', 'away_team')

    def get_latest_predictions(self, now: datetime) -> QuerySet:
        return self.filter(
                pub_date__lte=now,
            ).order_by('-pub_date')[:5].select_related('home_team', 'away_team', 'tournament')

    def get_latest_results(self) -> QuerySet:
        return self.filter(
                status='Match Finished',
            ).order_by('-game_date')[:5].select_related('home_team', 'away_team', 'tournament')

    def get_predictions_list(self, filter: dict, team_filter: Q) -> QuerySet:
        return self.filter(team_filter).filter(**filter).annotate(
                outcome_odds=KeyTextTransform('Match Winner', 'game_odds')
            ).order_by('-pub_date').select_related('home_team', 'away_team')

    def get_scores(self, user_timezone: str, target_time: datetime) -> QuerySet:
        return self.filter(
                game_date__gte=timezone(user_timezone).localize(datetime.combine(target_time, target_time.min.time())),
                game_date__lte=timezone(user_timezone).localize(datetime.combine(target_time, target_time.max.time())),
            ).order_by('tournament__pseudonym', 'game_date').select_related('tournament')

    def get_standings_next_games(self, obj: Tournament) -> QuerySet:
        return self.filter(
                tournament=obj,
                status__in=['Not Started', 'First Half', 'Halftime', 'Second Half', 'Time to be defined'],
            ).order_by('game_date')[:20]

    def get_standings_latest_games(self, obj: Tournament) -> QuerySet:
        return self.filter(tournament=obj, status='Match Finished').order_by('game_date')[:20]

    def get_team_next_games(self, team: Team, now: datetime) -> QuerySet:
        return self.filter(Q(home_team=team)|Q(away_team=team), game_date__gte=now,
            ).order_by('game_date')[:3].select_related('home_team', 'away_team', 'tournament')

    def get_team_latest_games(self, team: Team) -> QuerySet:
        return self.filter(Q(home_team=team)|Q(away_team=team), status='Match Finished',
            ).order_by('-game_date')[:10].select_related('home_team', 'away_team', 'tournament',
            ).annotate(outcome_odds=KeyTextTransform('Match Winner', 'game_odds'))


class Game(UUIDMixin):
    api_game_id = models.IntegerField(unique=True)
    game_date = models.DateTimeField()
    venue = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    referee = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    season = models.IntegerField(blank=True, null=True)
    round = models.CharField(max_length=255)
    home_team = models.ForeignKey(
        'Team', on_delete=models.CASCADE, related_name='home_team',
        )
    away_team = models.ForeignKey(
        'Team', on_delete=models.CASCADE, related_name='away_team',
        )
    home_goals_ht = models.IntegerField(blank=True, null=True)
    away_goals_ht = models.IntegerField(blank=True, null=True)
    home_goals_ft = models.IntegerField(blank=True, null=True)
    away_goals_ft = models.IntegerField(blank=True, null=True)
    home_goals_et = models.IntegerField(blank=True, null=True)
    away_goals_et = models.IntegerField(blank=True, null=True)
    home_goals_pen = models.IntegerField(blank=True, null=True)
    away_goals_pen = models.IntegerField(blank=True, null=True)
    game_odds = models.JSONField(blank=True, null=True)
    home_team_stats = models.JSONField(blank=True, null=True)
    away_team_stats = models.JSONField(blank=True, null=True)
    game_events = models.JSONField(blank=True, null=True)
    lineups = models.JSONField(blank=True, null=True)
    home_team_defence = models.IntegerField(blank=True, null=True)
    home_team_attack = models.IntegerField(blank=True, null=True)
    away_team_defence = models.IntegerField(blank=True, null=True)
    away_team_attack = models.IntegerField(blank=True, null=True)
    home_team_class = models.IntegerField(blank=True, null=True)
    away_team_class = models.IntegerField(blank=True, null=True)
    prediction = models.JSONField(blank=True, null=True)
    preview = models.JSONField(blank=True, null=True)
    report = models.JSONField(blank=True, null=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    home_team_last_games = models.JSONField(blank=True, null=True)
    away_team_last_games = models.JSONField(blank=True, null=True)
    home_team_last_same_games = models.JSONField(blank=True, null=True)
    away_team_last_same_games = models.JSONField(blank=True, null=True)
    home_team_last_tour_games = models.JSONField(blank=True, null=True)
    away_team_last_tour_games = models.JSONField(blank=True, null=True)
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True)

    objects = GameManager()

    def get_absolute_url(self):
        return reverse('preview', args=[self.slug])

    class Meta:
        db_table = 'content\".\"game'
        ordering = ['-game_date']
