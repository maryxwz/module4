from django.urls import path

from backoffice import views

urlpatterns = [
    path(
        'user-reports/',
         views.user_reports_list,
         name='user_reports_list'
    ),
    path(
        'settings/',
        views.settings,
        name='settings'
    ),
    path(
        'report/<str:username>/',
        views.report_user,
        name='report_user'
    ),
]
