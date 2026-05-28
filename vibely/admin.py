from django.contrib import admin
from .models import Profile, Post, Comment, Like, Follow, Message

# Customizing how Posts look in the admin panel table
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_time_capsule', 'expiration_time')
    list_filter = ('is_time_capsule', 'created_at')
    search_fields = ('user__username', 'caption')

# Customizing how Messages look in the admin panel table
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'body')

# Register your models to make them visible in the dashboard
admin.site.register(Profile)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Message, MessageAdmin)


# Register your models here.
