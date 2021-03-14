from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

# from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


# @cache_page(20)
class PostsListView(ListView):
    model = Post
    template_name = "index.html"
    paginate_by = 5
    context_object_name = "posts"


class GroupPostsListView(ListView):
    model = Post
    template_name = "group.html"
    paginate_by = 5
    context_object_name = "page"

    def get_queryset(self):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
        return post_list


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "new_post.html"
    extra_context = {
        "edit": False
    }

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Пост добавлен",
            extra_tags='success'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("index")


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


class PostDetailView(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"
    extra_context = {
        "form": CommentForm(),
    }

    def get_queryset(self):
        post = Post.objects.filter(id=self.kwargs['post_id'],
                                   author__username=self.kwargs['username'])
        return post


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "new_post.html"
    pk_url_kwarg = "post_id"
    extra_context = {
        "edit": True
    }

    def get_context_data(self, **kwargs):
        messages.add_message(
            self.request,
            messages.INFO,
            f"Пост обновлен",
            extra_tags='info'
        )
        return super().get_context_data(**kwargs)

    @property
    def success_url(self):
        return reverse('post', kwargs={"username": self.object.author,
                                       "post_id": self.object.id})


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
