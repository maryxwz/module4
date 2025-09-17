from django.urls import path
from . import views

app_name = 'direct'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('toggle-pin/', views.toggle_pin, name='toggle_pin'),
    path('create/', views.create_direct, name='create_direct'),
    path('reorder_pins/', views.reorder_pins, name='reorder_pins'),
    path('get-friends/', views.get_friends, name='get_friends'),
    path('create-group/', views.create_group, name='create_group'),
    path('t/<str:kind>/<uuid:chat_id>/', views.thread_view, name='thread'),
    path('t/<str:kind>/<uuid:chat_id>/messages/', views.thread_messages_api, name='thread_messages_api'),
]
