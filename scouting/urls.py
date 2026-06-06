from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/create/', views.create_player_profile, name='create_player_profile'),
    path('profile/edit/', views.edit_player_profile, name='edit_player_profile'),
    path('profile/stats/', views.update_stats, name='update_stats'),
    path('profile/video/upload/', views.upload_video, name='upload_video'),
    path('profile/video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('players/', views.player_list, name='player_list'),
    path('players/<int:pk>/', views.player_detail, name='player_detail'),
]