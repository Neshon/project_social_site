from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


# @cache_page(20)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "index.html",
                  {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "group.html",
                  {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    form = PostForm()
    return render(request, "new_post.html", {"form": form, "edit": False})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author.id).order_by("-pub_date").all()
    followers = Follow.objects.filter(author=author).count()
    following = Follow.objects.filter(user=author).count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "profile.html",
                  {"author": author,
                   "page": page,
                   "post_list": post_list,
                   "paginator": paginator,
                   "followers": followers,
                   "following": following})


def post_view(request, username, post_id):
    # author = get_object_or_404(User, username=username)
    # post = Post.objects.get(id=post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    count_post = Post.objects.filter(author=post.author).count()
    form = CommentForm(instance=None)
    items = post.comments.all()
    return render(request,
                  "post.html",
                  {"author": post.author,
                   "post": post,
                   "form": form,
                   "items": items,
                   "count_post": count_post})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    # if request.user.username != post.author:
    #     return redirect("profile", username=post.author)
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect("post", username=author.username, post_id=post.id)
    form = PostForm(instance=post)
    return render(request,
                  "new_post.html",
                  {"form": form, "post": post, "edit": True})


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    items = post.comments.all()
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'post.html', {'form': form, 'items': items, 'post': post})


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    favorite_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(favorite_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request,
                  "follow.html",
                  {"page": page, "paginator": paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)