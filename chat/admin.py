from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'created', 'message']
    list_filter = ['room', 'user']
    search_fields = ['room', 'message']

    def has_add_permission(self, request):
        return False