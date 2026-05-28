from django.urls import path
from . import views

urlpatterns = [
    # Core Feed & Authentication
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    
    # Discovery & Creation
    path('explore/', views.explore, name='explore'),
    path('post/new/', views.create_post, name='create_post'),
    
    # Post Interactions
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/repost/', views.repost_post, name='repost_post'),
    
    # User Profiles & Relationship Toggles
    path('user/<str:username>/', views.profile, name='profile'),
    path('user/<str:username>/toggle-follow/', views.toggle_follow, name='toggle_follow'),
    
    # Direct Messages Engine
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<str:username>/', views.chat_room, name='chat_room'),
    path('user/profile/edit/', views.edit_profile, name='edit_profile'),
    path('message/<str:username>/', views.send_message, name='send_message'),
]