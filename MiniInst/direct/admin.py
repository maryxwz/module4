from django.contrib import admin
from direct.models import Direct, DirectMessage, GroupChat, GroupMessage

@admin.register(Direct)
class DirectAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    ordering = ('-created_at',)

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'direct', 'sender', 'message', 'created_at')
    search_fields = ('sender__username', 'message')
    ordering = ('-created_at',)

@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_chat', 'sender', 'message', 'created_at')
    search_fields = ('sender__username', 'message')
    ordering = ('-created_at',)

