from datetime import datetime, timedelta

import django.utils.timezone
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView
from pytz import timezone

from arena.models import Game, Team, Tournament


class IndexView(TemplateView):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        user_timezone = self.request.session.get('timezone', 'utc')
        now = set_timezone(user_timezone)
        context = super(IndexView, self).get_context_data(**kwargs)
        context['user_timezone'] = user_timezone

        next_games = Game.objects.get_next_games(now=now)
        main_games = Game.objects.get_main_games(now=now)
        latest_predictions = Game.objects.get_latest_predictions(now=now)
        latest_results = Game.objects.get_latest_results()

        context.update(
            {
                'next_games': next_games,
                'main_games': main_games,
                'latest_predictions': latest_predictions,
                'latest_results': latest_results,
            }
        )

        return context


class PredictionsView(ListView):
    paginate_by = 20
    template_name = 'pages/predictions.html'

    def get_queryset(self):
        user_timezone = self.request.session.get('timezone', 'utc')
        now = set_timezone(user_timezone)
        filter = {'pub_date__lte': now}
        team_filter = Q()

        if self.request.GET.get('team'):
            team = self.request.GET.get('team')
            team_filter = Q(home_team__slug=team) | Q(away_team__slug=team)

        elif self.request.GET.get('league'):
            league = self.request.GET.get('league')
            filter.update({'tournament__slug': league})

        elif self.request.GET.get('date'):
            date = self.request.GET.get('date')
            match date:
                case 'tomorrow':
                    filter_date = now + timedelta(days=1)
                case 'after_tomorrow':
                    filter_date = now + timedelta(days=2)
                case _:
                    filter_date = now
            filter.update({
                'game_date__gte': datetime.combine(filter_date, filter_date.min.time()).astimezone(),
                'game_date__lte': datetime.combine(filter_date, filter_date.max.time()).astimezone(),
            })

        return Game.objects.get_predictions_list(filter=filter, team_filter=team_filter)


class PreviewView(DetailView):
    model = Game
    template_name = 'pages/preview.html'

    def get_context_data(self, **kwargs):
        user_timezone = self.request.session.get('timezone', 'utc')
        set_timezone(user_timezone)
        context = super(PreviewView, self).get_context_data(**kwargs)
        return context


class ScoresView(ListView):
    template_name = 'pages/scores.html'

    def get_queryset(self):
        offset = 0
        if self.request.GET.get('date') == 'tomorrow':
            offset = 1
        elif self.request.GET.get('date') == 'yesterday':
            offset = -1

        user_timezone = self.request.session.get('timezone', 'utc')
        now = set_timezone(user_timezone)
        target_time = now + timedelta(days=offset)

        return Game.objects.get_scores(user_timezone=user_timezone, target_time=target_time)


class StandingsView(DetailView):
    model = Tournament
    template_name = 'pages/standings.html'

    def get_context_data(self, **kwargs):
        user_timezone = self.request.session.get('timezone', 'utc')
        set_timezone(user_timezone)
        context = super(StandingsView, self).get_context_data(**kwargs)
        context['next_games'] = Game.objects.get_standings_next_games(obj=context['object'])
        context['latest_games'] = Game.objects.get_standings_latest_games(obj=context['object'])
        context['stats'] = 'stats_all'
        if self.request.GET.get('stats') == 'home':
            context['stats'] = 'stats_home'
        elif self.request.GET.get('stats') == 'away':
            context['stats'] = 'stats_away'

        return context


class ReportView(DetailView):
    model = Game
    template_name = 'pages/report.html'

    def lineups(self) -> tuple:
        subst_in = {}
        subst_out = {}
        for event in self.object.game_events:
            if event['type'] == 'subst':
                subst_in[event['assist']['id']] = f"for {event['player']['name']} {event['time']['elapsed']}'"
                subst_out[event['player']['id']] = f"{event['time']['elapsed']}'"
        return subst_in, subst_out

    def get_context_data(self, **kwargs):
        user_timezone = self.request.session.get('timezone', 'utc')
        set_timezone(user_timezone)
        context = super(ReportView, self).get_context_data(**kwargs)
        context['subst_in'], context['subst_out'] = self.lineups()
        return context


class TeamView(DetailView):
    model = Team
    template_name = 'pages/team.html'

    def get_context_data(self, **kwargs):
        user_timezone = self.request.session.get('timezone', 'utc')
        now = set_timezone(user_timezone)
        context = super(TeamView, self).get_context_data(**kwargs)

        context['next_games'] = Game.objects.get_team_next_games(team=self.object, now=now)
        latest_games = Game.objects.get_team_latest_games(team=self.object)
        context['latest_games'] = latest_games
        context['team_stats'] = Team.get_team_stats(obj=self.object, latest_games=latest_games)

        return context


class TeamsView(TemplateView):
    template_name = 'pages/teams.html'

    def get_context_data(self, **kwargs):
        user_timezone = self.request.session.get('timezone', 'utc')
        set_timezone(user_timezone)
        context = super(TeamsView, self).get_context_data(**kwargs)
        league = self.request.GET.get('league', 'england-premier-league')
        sort = self.request.GET.get('sort', 'defence')
        context['teams'] = Team.objects.filter(league__slug=league).order_by(f'-{sort}')
        context['user_timezone'] = user_timezone

        return context


def set_timezone(user_timezone: str) -> datetime:
    tz = timezone(user_timezone)
    django.utils.timezone.activate(tz)

    return timezone(user_timezone).localize(datetime.now())


def page_not_found_view(request, exception):
    return render(request, 'pages/404.html', status=404)


def error_view(request, exception=None):
    return render(request, "pages/50x.html", status=500)
