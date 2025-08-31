from django.urls import path

from backoffice import views

urlpatterns = [
    path(
        'user-reports/',
         views.user_reports_list,
         name='user_reports_list'
    ),
]
