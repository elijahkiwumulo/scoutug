from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, PlayerProfile, PlayerStats, PlayerVideo, PlayerRating


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [('player', 'Player'), ('scout', 'Scout'), ('coach', 'Coach')]
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    phone = forms.CharField(max_length=20, required=False)
    district = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone', ''),
                district=self.cleaned_data.get('district', ''),
            )
        return user


class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = ['position', 'preferred_foot', 'age', 'height_cm', 'weight_kg',
                  'district', 'school_or_club', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = ['matches_played', 'goals', 'assists', 'clean_sheets',
                  'yellow_cards', 'red_cards', 'speed_kmh']


class PlayerVideoForm(forms.ModelForm):
    class Meta:
        model = PlayerVideo
        fields = ['title', 'video_file', 'video_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PlayerRatingForm(forms.ModelForm):
    class Meta:
        model = PlayerRating
        fields = ['pace', 'technique', 'physicality', 'teamwork', 'positioning', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'pace': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'technique': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'physicality': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'teamwork': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'positioning': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


class PlayerSearchForm(forms.Form):
    POSITION_CHOICES = [('', 'All Positions')] + PlayerProfile.POSITION_CHOICES
    name = forms.CharField(required=False, label='Player Name')
    position = forms.ChoiceField(choices=POSITION_CHOICES, required=False)
    district = forms.CharField(required=False)
    min_age = forms.IntegerField(required=False, min_value=10, max_value=40, label='Min Age')
    max_age = forms.IntegerField(required=False, min_value=10, max_value=40, label='Max Age')



class StatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        fields = "__all__"

        widgets = {
            'matches_played': forms.NumberInput(attrs={'class': 'form-control'}),
            'goals': forms.NumberInput(attrs={'class': 'form-control'}),
            'assists': forms.NumberInput(attrs={'class': 'form-control'}),
            'clean_sheets': forms.NumberInput(attrs={'class': 'form-control'}),
            'yellow_cards': forms.NumberInput(attrs={'class': 'form-control'}),
            'red_cards': forms.NumberInput(attrs={'class': 'form-control'}),
            'speed_kmh': forms.NumberInput(attrs={'class': 'form-control'}),
        }

  