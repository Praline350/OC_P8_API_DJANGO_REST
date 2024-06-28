from django.contrib import admin

from authentication.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'can_be_contacted', 'can_data_be_shared')
