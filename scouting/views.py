from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .models import PlayerProfile, PlayerStats, PlayerVideo, PlayerRating, UserProfile
from .forms import (RegisterForm, PlayerProfileForm, PlayerStatsForm,
                    PlayerVideoForm, PlayerRatingForm, PlayerSearchForm)

# Create your views here.
def home(request):
    total_players = PlayerProfile.objects.count()
    recent_players = PlayerProfile.objects.order_by('-created_at')[:6]
    return render(request, 'scouting/home.html', {
        'total_players': total_players,
        'recent_players': recent_players,
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'scouting/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'scouting/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    profile = request.user.profile
    context = {'profile': profile}
    if profile.role == 'player':
        try:
            player = request.user.player_profile
            context['player'] = player
            context['has_stats'] = hasattr(player, 'stats')
            context['videos'] = player.videos.all()
            context['ratings'] = player.ratings.all()
        except PlayerProfile.DoesNotExist:
            context['player'] = None
    else:
        context['recent_players'] = PlayerProfile.objects.order_by('-created_at')[:8]
        context['total_players'] = PlayerProfile.objects.count()
        context['total_ratings'] = PlayerRating.objects.filter(evaluator=request.user).count()
    return render(request, 'scouting/dashboard.html', context)


@login_required
def create_player_profile(request):
    if hasattr(request.user, 'player_profile'):
        return redirect('edit_player_profile')
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Player profile created!')
            return redirect('dashboard')
    else:
        form = PlayerProfileForm()
    return render(request, 'scouting/player_form.html', {'form': form, 'title': 'Create Profile'})


@login_required
def edit_player_profile(request):
    player = get_object_or_404(PlayerProfile, user=request.user)
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')
    else:
        form = PlayerProfileForm(instance=player)
    return render(request, 'scouting/player_form.html', {'form': form, 'title': 'Edit Profile'})


@login_required
def update_stats(request):
    player = get_object_or_404(PlayerProfile, user=request.user)
    stats = getattr(player, 'stats', None)
    if request.method == 'POST':
        form = PlayerStatsForm(request.POST, instance=stats)
        if form.is_valid():
            stat_obj = form.save(commit=False)
            stat_obj.player = player
            stat_obj.save()
            messages.success(request, 'Stats updated!')
            return redirect('dashboard')
    else:
        form = PlayerStatsForm(instance=stats)
    return render(request, 'scouting/stats_form.html', {'form': form})


@login_required
def upload_video(request):
    player = get_object_or_404(PlayerProfile, user=request.user)
    if request.method == 'POST':
        form = PlayerVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.player = player
            video.save()
            messages.success(request, 'Video uploaded!')
            return redirect('dashboard')
    else:
        form = PlayerVideoForm()
    return render(request, 'scouting/video_form.html', {'form': form})


@login_required
def delete_video(request, pk):
    video = get_object_or_404(PlayerVideo, pk=pk, player__user=request.user)
    video.delete()
    messages.success(request, 'Video deleted.')
    return redirect('dashboard')


def player_list(request):
    players = PlayerProfile.objects.select_related('user', 'stats').all()
    form = PlayerSearchForm(request.GET)
    if form.is_valid():
        name = form.cleaned_data.get('name')
        position = form.cleaned_data.get('position')
        district = form.cleaned_data.get('district')
        min_age = form.cleaned_data.get('min_age')
        max_age = form.cleaned_data.get('max_age')
        if name:
            players = players.filter(
                Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name)
            )
        if position:
            players = players.filter(position=position)
        if district:
            players = players.filter(district__icontains=district)
        if min_age:
            players = players.filter(age__gte=min_age)
        if max_age:
            players = players.filter(age__lte=max_age)
    return render(request, 'scouting/player_list.html', {'players': players, 'form': form})


def player_detail(request, pk):
    player = get_object_or_404(PlayerProfile.objects.select_related('user', 'stats'), pk=pk)
    user_rating = None
    rating_form = None
    if request.user.is_authenticated:
        try:
            user_rating = PlayerRating.objects.get(player=player, evaluator=request.user)
        except PlayerRating.DoesNotExist:
            pass
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in ('scout', 'coach'):
            if request.method == 'POST':
                form = PlayerRatingForm(request.POST, instance=user_rating)
                if form.is_valid():
                    rating = form.save(commit=False)
                    rating.player = player
                    rating.evaluator = request.user
                    rating.save()
                    messages.success(request, 'Rating submitted!')
                    return redirect('player_detail', pk=pk)
            else:
                form = PlayerRatingForm(instance=user_rating)
            rating_form = form
    return render(request, 'scouting/player_detail.html', {
        'player': player,
        'ratings': player.ratings.select_related('evaluator').all(),
        'user_rating': user_rating,
        'rating_form': rating_form,
    })
  try:
    profile = request.user.profile
except UserProfile.DoesNotExist:
    messages.error(request, "Profile not found. Please contact the administrator.")
    return redirect('home')
  user = form.save()
login(request, user)
return redirect('dashboard')


user = form.save()

UserProfile.objects.create(
    user=user,
    role='player'  # or your default role
)

login(request, user)
return redirect('dashboard')
