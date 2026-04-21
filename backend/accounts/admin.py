from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import RefreshToken, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role", {"fields": ("role", "display_name", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "jti", "expires_at", "revoked_at", "created_at")
    readonly_fields = ("jti", "token_hash", "created_at", "last_used_at")
    search_fields = ("user__username", "jti")
