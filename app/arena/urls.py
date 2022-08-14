from django.urls import path

from arena import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('previews', views.PredictionsView.as_view(), name='predictions'),
    path('previews/<slug:slug>', views.PreviewView.as_view(), name='preview'),
    path('scores', views.ScoresView.as_view(), name='scores'),
    path('standings/<slug:slug>', views.StandingsView.as_view(), name='standings'),
    path('scores/<slug:slug>', views.ReportView.as_view(), name='report'),
    path('teams/<slug:slug>', views.TeamView.as_view(), name='team'),
    path('teams', views.TeamsView.as_view(), name='teams'),
]
