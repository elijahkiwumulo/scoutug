from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile, PlayerProfile, PlayerStats, PlayerVideo, PlayerRating

admin.site.site_header = "Football Talent Scout Admin"
admin.site.site_title = "Scout Admin"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'district', 'phone']
    list_filter = ['role']

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'age', 'district', 'school_or_club', 'average_rating']
    list_filter = ['position', 'preferred_foot', 'district']
    search_fields = ['user__first_name', 'user__last_name', 'district', 'school_or_club']

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'matches_played', 'goals', 'assists', 'clean_sheets']

@admin.register(PlayerVideo)
class PlayerVideoAdmin(admin.ModelAdmin):
    list_display = ['player', 'title', 'uploaded_at']

@admin.register(PlayerRating)
class PlayerRatingAdmin(admin.ModelAdmin):
    list_display = ['player', 'evaluator', 'overall_score', 'rated_at']
