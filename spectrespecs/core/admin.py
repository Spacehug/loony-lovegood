from django.contrib import admin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter


from core.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "gid",
        "has_messages",
        "created_at",
        "grace_at",
    )
    list_display_links = (
        "uid",
        "gid",
        "has_messages",
        "created_at",
        "grace_at",
    )
    search_fields = ("uid", "gid")
    list_filter = (
        "has_messages",
        ("created_at", DateRangeFilter),
        ("grace_at", DateTimeRangeFilter),
    )
