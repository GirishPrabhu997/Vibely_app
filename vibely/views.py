from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Post, Follow, Like, Comment, Message
import os

def purge_expired_posts():
    """Removes posts from the DB if their unique timer has passed."""
    Post.objects.filter(is_time_capsule=True, expiration_time__lt=timezone.now()).delete()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    django_logout(request)
    return redirect('login')

@login_required
def repost_post(request, post_id):
    original_post = get_object_or_404(Post, id=post_id)
    
    # Prevent a user from infinitely reposting their own exact same repost duplicate
    if original_post.user == request.user and original_post.parent_post is not None:
        return redirect('index')
        
    # Create the new feed item pointing to the parent asset
    Post.objects.create(
        user=request.user,
        parent_post=original_post if original_post.parent_post is None else original_post.parent_post,
        caption=original_post.caption
    )
    return redirect('index')

@login_required
def index(request):
    purge_expired_posts()
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user_id__in=list(following_users) + [request.user.id])
    return render(request, 'index.html', {'posts': posts})

@login_required
def explore(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(username__icontains=search_query).exclude(id=request.user.id) if search_query else None
    all_posts = Post.objects.all().exclude(user=request.user)
    return render(request, 'explore.html', {'all_posts': all_posts, 'users': users, 'search_query': search_query})

@login_required
def create_post(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption')
        capsule_mode = request.POST.get('capsule_mode')
        post = Post(user=request.user, image=image if image else None, caption=caption)
        
        if capsule_mode and capsule_mode != 'permanent':
             post.is_time_capsule = True
             post.expiration_time = timezone.now() + timedelta(hours=int(capsule_mode))
        post.save()
        return redirect('index')
    return render(request, 'create_post.html')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_filter = Like.objects.filter(post=post, user=request.user)
    if like_filter.exists():
        like_filter.delete()
    else:
        Like.objects.create(post=post, user=request.user)
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(post=post, user=request.user, text=comment_text)
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(user=user_profile)
    is_following = Follow.objects.filter(follower=request.user, following=user_profile).exists()
    
    context = {
        'user_profile': user_profile,
        'posts': user_posts,
        'is_following': is_following,
        'follower_count': Follow.objects.filter(following=user_profile).count(),
        'following_count': Follow.objects.filter(follower=user_profile).count(),
        'profile_user': user_profile,
    }
    return render(request, 'profile.html', context)

@login_required
def toggle_follow(request, username):
    """Handles both follow and unfollow requests securely using the Follow intermediary model."""
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)
        
        if target_user != request.user:
            follow_relation = Follow.objects.filter(follower=request.user, following=target_user)
            if follow_relation.exists():
                # Unfollow
                follow_relation.delete()
            else:
                # Follow
                Follow.objects.create(follower=request.user, following=target_user)
                
    return redirect('profile', username=username)

@login_required
def inbox(request):
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    chat_partners_ids = set()
    for msg in messages:
        chat_partners_ids.add(msg.sender.id if msg.sender != request.user else msg.receiver.id)
            
    chat_partners = User.objects.filter(id__in=chat_partners_ids)
    return render(request, 'inbox.html', {'chat_partners': chat_partners})

@login_required
# Updated imports: Ensure 'media' is handled
# Add this to your imports if not present: from django.db import models

@login_required
def chat_room(request, username):
    recipient = get_object_or_404(User, username=username)
    
    # Handle incoming messages (Text + Media)
    if request.method == 'POST':
        content = request.POST.get('content')
        media = request.FILES.get('media') # Grabs the file
        
        # Only create if there is content or media
        if content or media:
            Message.objects.create(
                sender=request.user, 
                receiver=recipient, 
                content=content, 
                media=media
            )
            # Redirect to same page to prevent form resubmission
            return redirect('chat_room', username=username)

    # Fetch and display chat history
    chat_thread = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=recipient)) | 
        (Q(sender=recipient) & Q(receiver=request.user))
    ).order_by('created_at') # Ensures chronological order
    
    return render(request, 'chat.html', {
        'chat_thread': chat_thread, 
        'recipient': recipient
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.image:
        if os.path.isfile(post.image.path):
            # Optionally, close the file handle if it exists
            post.image.delete(save=False) 
    post.delete()
    return redirect('index')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            user_profile = request.user.profile
            # Optional: Delete old image from disk if it exists
            if user_profile.image and os.path.exists(user_profile.image.path):
                os.remove(user_profile.image.path)
            
            user_profile.image = profile_image
            user_profile.save()
            return redirect('profile', username=request.user.username)
            
    return render(request, 'edit_profile.html') # Create this template if you want a dedicated edit page
