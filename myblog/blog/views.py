# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Post, Comment, Category, Tag, UserProfile
from .forms import CommentForm, PostForm, CustomUserCreationForm, UserProfileForm, UserProfileExtraForm
from django.core.paginator import Paginator
import uuid
from django.template.defaultfilters import slugify
from django.db.models import Q

def create_default_categories_and_tags():
    """Создает категории и теги по умолчанию если их нет"""
    categories = ['Программирование', 'Дизайн', 'Маркетинг', 'Путешествия', 'Кулинария']
    for cat_name in categories:
        category, created = Category.objects.get_or_create(name=cat_name)
        if created and not category.slug:
            category.slug = slugify(cat_name) + '-' + uuid.uuid4().hex[:6]
            category.save()
    
    tags = ['django', 'python', 'web', 'development', 'design', 'cooking', 'travel']
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        if created and not tag.slug:
            tag.slug = slugify(tag_name) + '-' + uuid.uuid4().hex[:6]
            tag.save()

def post_list(request):
    # Создаем категории по умолчанию для главной страницы
    create_default_categories_and_tags()
    
    posts_list = Post.objects.filter(is_published=True).order_by('-published_date')
    categories = Category.objects.all()
    
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'categories': categories
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(approved_comment=True)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, 'Ваш комментарий был добавлен и ожидает модерации.')
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, is_published=True).order_by('-published_date')
    return render(request, 'blog/category_posts.html', {
        'category': category,
        'posts': posts
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('post_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('post_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'blog/login.html')

def user_logout(request):
    auth_logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return render(request, 'blog/logout.html')

@login_required
def create_post(request):
    # Создаем категории и теги по умолчанию перед отображением формы
    create_default_categories_and_tags()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.is_published:
                post.published_date = timezone.now()
            post.save()
            form.save_m2m()  # Для сохранения ManyToMany полей (тегов)
            messages.success(request, 'Пост успешно создан!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_date')
    return render(request, 'blog/my_posts.html', {'posts': posts})

@login_required
def profile(request):
    return render(request, 'blog/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = UserProfileExtraForm(request.POST, request.FILES, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = UserProfileExtraForm(instance=request.user.userprofile)
    
    return render(request, 'blog/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важно!
            messages.success(request, 'Ваш пароль был успешно изменен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'blog/change_password.html', {'form': form})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user, is_published=True).order_by('-published_date')
    
    return render(request, 'blog/user_profile.html', {
        'profile_user': user,
        'posts': posts
    })
from django.db.models import Q

def search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Поиск по постам
        post_results = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True
        ).distinct().order_by('-published_date')
        
        # Поиск по пользователям
        user_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()
        
        results = {
            'posts': post_results,
            'users': user_results,
            'query': query
        }
    
    return render(request, 'blog/search_results.html', results)

def user_search(request):
    query = request.GET.get('q', '')
    users = User.objects.all()
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()
    
    return render(request, 'blog/user_search.html', {
        'users': users,
        'query': query
    })