from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    is_private = models.BooleanField(default=False)
    followers_only = models.BooleanField(default=False)
    
    # This line alone handles both followers and following
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ✅ Auto-create or update profile when user is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    media = models.FileField(upload_to='posts/', blank=True, null=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    

    def is_image(self):
        return self.media.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))

    def is_video(self):
        return self.media.name.lower().endswith(('.mp4', '.webm', '.ogg'))

    def __str__(self):
        return f"{self.author.username}'s Post"
    
    @property
    def top_comments(self):
        return self.comments.filter(parent=None).order_by('created_at')
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment by {self.user.username}'
    
    def is_reply(self):
        return self.parent is not None
    
    
    
class Follower(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

