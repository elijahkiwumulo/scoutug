from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('scout', 'Scout'),
        ('coach', 'Coach'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"


class PlayerProfile(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('CB', 'Centre Back'),
        ('LB', 'Left Back'),
        ('RB', 'Right Back'),
        ('CDM', 'Defensive Midfielder'),
        ('CM', 'Central Midfielder'),
        ('CAM', 'Attacking Midfielder'),
        ('LW', 'Left Winger'),
        ('RW', 'Right Winger'),
        ('ST', 'Striker'),
        ('CF', 'Centre Forward'),
    ]
    FOOT_CHOICES = [('left', 'Left'), ('right', 'Right'), ('both', 'Both')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    preferred_foot = models.CharField(max_length=5, choices=FOOT_CHOICES, default='right')
    age = models.PositiveIntegerField(default=18)
    height_cm = models.PositiveIntegerField(default=170)
    weight_kg = models.PositiveIntegerField(default=65)
    district = models.CharField(max_length=100, blank=True)
    school_or_club = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='player_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} – {self.position}"

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.overall_score() for r in ratings) / ratings.count(), 1)
        return None


class PlayerStats(models.Model):
    player = models.OneToOneField(PlayerProfile, on_delete=models.CASCADE, related_name='stats')
    matches_played = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    clean_sheets = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    speed_kmh = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stats – {self.player.user.get_full_name()}"


class PlayerVideo(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='player_videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or other video link")
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.player.user.get_full_name()}"


class PlayerRating(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='ratings')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    pace = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    technique = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    physicality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    teamwork = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    positioning = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comments = models.TextField(blank=True)
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'evaluator')

    def overall_score(self):
        return round((self.pace + self.technique + self.physicality + self.teamwork + self.positioning) / 5, 1)

    def __str__(self):
        return f"Rating by {self.evaluator.get_full_name()} for {self.player.user.get_full_name()}"
