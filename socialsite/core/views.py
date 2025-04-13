# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile, Post, Comment
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .forms import PostForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from core.utils import parse_caption
import re
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from .models import Follower
from django.db.models import Prefetch
from django.http import Http404



def home(request):
    return render(request, 'core/home.html')

def index(request):
    return render(request, 'core/index.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')  # or redirect to profile/dashboard
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            # You can integrate email logic here later
            messages.success(request, "Password reset link sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")

    return render(request, 'core/password_reset.html')


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'core/edit_profile.html', {'form': form})


@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()  # Deletes user + profile due to CASCADE
        messages.success(request, "Your profile has been deleted.")
        return redirect('home')
    return render(request, 'core/delete_profile.html')

@login_required
def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    # Check visibility
    if profile.is_private and request.user.profile not in profile.followers.all() and request.user != profile.user:
        private = True
    else:
        private = False

    # Fetch user posts
    posts = user.posts.all().order_by('-created_at')

    # Check if the logged-in user is following this profile
    is_following = Follower.objects.filter(following=user, follower=request.user).exists()
    followers_count = Follower.objects.filter(following=user).count()
    following_count = Follower.objects.filter(follower=user).count()

    is_owner = request.user == profile.user
    is_follower = profile.followers.filter(id=request.user.profile.id).exists()

    is_private = profile.is_private and not is_owner and not is_follower

    if is_private:
        return render(request, 'core/private_profile.html', {
            'profile': profile,
            'is_following': False,  # Not following, so can't view
        })


    context = {
        'posts': posts,
        'profile': profile,
        'is_private': private,
        'user_profile': user,
        'followers_count': profile.followers.count(),
        'following_count': profile.following.count(),
        'is_following': profile in request.user.profile.following.all() if request.user.is_authenticated else False,
    }
    return render(request, 'core/view_profile.html', context)

 
class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse('view_profile', kwargs={'username': self.request.user.username})
    
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post was created successfully!')
            return redirect('view_profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'core/create_post.html', {'form': form})

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)  
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    parsed_caption = parse_caption(post.caption)
    
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments,
        'parsed_caption': parsed_caption,
    })


@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count(),
        })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('comment') or request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        if content:
            Comment.objects.create(user=request.user, post=post, content=content, parent=parent)
    return redirect('post_detail', post_id=post.id)

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.user == request.user or comment.post.author == request.user:
        comment.delete()
        messages.success(request, "Comment deleted.")
    else:
        messages.error(request, "You are not allowed to delete this comment.")

    return redirect('post_detail', post_id=post_id)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'core/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect('view_profile', username=request.user.username)

    return render(request, 'core/delete_post.html', {'post': post})

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)

    current_user_profile = request.user.profile
    profiles = Profile.objects.filter(user__in=users)

    return render(request, 'core/search_results.html', {
        'query': query,
        'profiles': profiles,
        'current_user_profile': current_user_profile,
    })

@login_required
def follow_user(request, username):
    target_profile = get_object_or_404(Profile, user__username=username)
    if request.user.profile != target_profile:
        if target_profile in request.user.profile.following.all():
            request.user.profile.following.remove(target_profile)
        else:
            request.user.profile.following.add(target_profile)
    return redirect('view_profile', username=username)

@login_required
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    request.user.profile.following.remove(target_profile)
    return redirect(request.META.get('HTTP_REFERER', 'view_profile'))

@login_required
def feed(request):
    # Get User objects from followed Profile objects
    following_profiles = request.user.profile.following.all()
    following_users = [profile.user for profile in following_profiles]

    posts = Post.objects.filter(author__in=following_users).select_related('author', 'author__profile').order_by('-created_at')
    return render(request, 'core/feed.html', {'posts': posts})

@require_POST
@login_required
def add_comment_feed(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get('parent_id')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        if content:
            Comment.objects.create(user=request.user, post=post, content=content, parent=parent)
            return redirect('feed')  # Or wherever your feed view name is

    return redirect('feed')

@require_POST
@login_required
def delete_comment_feed(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)

        if comment.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        comment.delete()
        return JsonResponse({'success': True})

    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found'}, status=404)

@login_required
def followers_list(request, username):
    try:
        target_user = get_object_or_404(User, username=username)
        target_profile = target_user.profile
        followers = Profile.objects.filter(following=target_profile)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('core/follow_list.html', {
                'users': followers
            })
            return JsonResponse({'html': html})
        else:
            raise Http404("Invalid request type.")
    except Exception as e:
        print("FOLLOWERS ERROR:", e)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def following_list(request, username):
    try:
        target_user = get_object_or_404(User, username=username)
        target_profile = target_user.profile
        following = target_profile.following.all()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('core/follow_list.html', {
                'users': following
            })
            return JsonResponse({'html': html})
        else:
            raise Http404("Invalid request type.")
    except Exception as e:
        print("FOLLOWING ERROR:", e)
        return JsonResponse({'error': str(e)}, status=500)
    
