from django.urls import path
from . import views
from .views import PostsListView, GroupPostsListView, PostDetailView, PostCreateView, PostUpdateView

urlpatterns = [
    path("", PostsListView.as_view(), name="index"),
    path("new/", PostCreateView.as_view(), name="new_post"),
    path("follow/", views.follow_index, name="follow_index"),
    path("group/<slug:slug>/", GroupPostsListView.as_view(), name="groups"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", PostDetailView.as_view(), name="post"),
    path("<str:username>/<int:post_id>/edit/",
         PostUpdateView.as_view(),
         name="post_edit"),
    path("<username>/<int:post_id>/comment/",
         views.add_comment,
         name="add_comment"),
    path("<str:username>/follow/",
         views.profile_follow,
         name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow,
         name="profile_unfollow"),
]
