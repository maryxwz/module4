from django.urls import path
from . import views

app_name = 'direct'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('t/<uuid:direct_id>/', views.thread_view, name='thread'),
    path('t/<uuid:direct_id>/messages/', views.thread_messages_api, name='thread_messages_api'),

]
