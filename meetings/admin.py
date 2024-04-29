from django.contrib import admin

from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        'creator', 'title', 'description', 'date', 'max_users',
    )
