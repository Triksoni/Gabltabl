from django.contrib import admin

# Register your models here.


# blog/admin.py

from django.contrib import admin
from .models import Category, Tag, Post, Comment

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'category')
    list_filter = ('published_date', 'category', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {} # Полезно для slug-полей (если будут)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_date', 'approved_comment')
    list_filter = ('approved_comment', 'created_date')
    search_fields = ('author', 'text')

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)