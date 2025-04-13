from django import forms
from .models import Profile, Post

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'profile_picture', 'is_private']

class PostForm(forms.ModelForm):
    caption = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'What’s on your mind?',
            'class': 'w-full p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )

    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['caption', 'media']