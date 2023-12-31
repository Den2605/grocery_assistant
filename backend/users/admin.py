from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "id",
        "username",
        "first_name",
        "last_name",
        "password",
    )
    search_fields = (
        "email",
        "username",
    )
    list_filter = (
        "email",
        "username",
    )
