# core/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (
    home,
    register_view,
    logout_view,
    password_reset_view,
    edit_profile,
    delete_profile,
    view_profile,
    add_comment_feed,
    CustomLoginView,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  
    path('logout/', logout_view, name='logout'),
    path('password-reset/', password_reset_view, name='password_reset'),

    path('profile/<str:username>/', view_profile, name='view_profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('delete-profile/', delete_profile, name='delete_profile'),

    path('create_post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
   
    path('search/', views.search_users, name='search_users'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),

    path('feed/', views.feed, name='feed'),
    path("post/<int:post_id>/comment/feed/", add_comment_feed, name="add_comment_feed"),
    path('comment/<int:comment_id>/delete/feed/', views.delete_comment_feed, name='delete_comment_feed'),

    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),

    









] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
