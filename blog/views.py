from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Category, Article, Comment, UserProfile
from .forms import RegisterForm, LoginForm, ArticleForm, CommentForm


# ──────────────────────────────────────────────
# Авторизація
# ──────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('blog:category_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.username}! Акаунт створено.')
            return redirect('blog:category_list')
    else:
        form = RegisterForm()
    return render(request, 'blog/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('blog:category_list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'З поверненням, {user.username}!')
            next_url = request.GET.get('next', '')
            return redirect(next_url) if next_url else redirect('blog:category_list')
        else:
            messages.error(request, 'Невірний логін або пароль.')
    else:
        form = LoginForm()
    return render(request, 'blog/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('blog:category_list')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_articles = Article.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'blog/auth/profile.html', {
        'profile': profile,
        'user_articles': user_articles,
    })


# ──────────────────────────────────────────────
# Категорії
# ──────────────────────────────────────────────

def category_list(request):
    categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__is_published=True))
    ).order_by('name')
    return render(request, 'blog/category_list.html', {
        'categories': categories,
        'total_articles': Article.objects.filter(is_published=True).count(),
        'total_categories': categories.count(),
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(
        category=category, is_published=True
    ).select_related('author').annotate(comment_count=Count('comments'))
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'articles': articles,
    })


# ──────────────────────────────────────────────
# Статті
# ──────────────────────────────────────────────

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    comments = article.comments.select_related('author').all()
    form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Увійдіть, щоб залишити коментар.')
            return redirect('blog:login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.author_name = request.user.username
            comment.save()
            messages.success(request, 'Коментар додано!')
            return redirect('blog:article_detail', pk=pk)

    # Передаємо прапор can_edit в шаблон
    can_edit = article.can_edit(request.user)

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form,
        'can_edit': can_edit,
    })


def _check_can_edit(request, article):
    """Перевірка прав. Повертає True або False і показує помилку."""
    if not request.user.is_authenticated:
        messages.error(request, 'Увійдіть в систему.')
        return False
    if not article.can_edit(request.user):
        messages.error(request, 'Ви не маєте прав для цієї дії.')
        return False
    return True


def _can_create(user):
    """Перевірка: чи може користувач створювати статті."""
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.can_create_article()


@login_required
def article_create(request):
    if not _can_create(request.user):
        messages.error(request, 'Тільки автори можуть створювати статті. Зверніться до адміністратора.')
        return redirect('blog:category_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Статтю створено!')
            return redirect('blog:article_detail', pk=article.pk)
    else:
        form = ArticleForm()

    return render(request, 'blog/article_form.html', {
        'form': form,
        'action': 'Створити статтю',
    })


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if not _check_can_edit(request, article):
        return redirect('blog:article_detail', pk=pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статтю оновлено!')
            return redirect('blog:article_detail', pk=pk)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'blog/article_form.html', {
        'form': form,
        'article': article,
        'action': 'Редагувати статтю',
    })


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if not _check_can_edit(request, article):
        return redirect('blog:article_detail', pk=pk)

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Статтю видалено.')
        return redirect('blog:category_list')

    return render(request, 'blog/article_confirm_delete.html', {'article': article})


# ──────────────────────────────────────────────
# Коментарі
# ──────────────────────────────────────────────

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    article_pk = comment.article.pk

    if not comment.can_delete(request.user):
        messages.error(request, 'Немає прав для видалення.')
        return redirect('blog:article_detail', pk=article_pk)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Коментар видалено.')

    return redirect('blog:article_detail', pk=article_pk)
