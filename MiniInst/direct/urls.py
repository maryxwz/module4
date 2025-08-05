from django.urls import path
from . import views

app_name = 'direct'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('<uuid:direct_id>/', views.thread, name='thread'),
]
