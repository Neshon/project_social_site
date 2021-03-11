from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    class Meta:
        ordering = ["-pub_date"]

    text = models.TextField(null=True)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              related_name="posts",
                              blank=True,
                              null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             related_name="comments")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(max_length=1000, null=True)
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["created"]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower"
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following"
                               )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="user_not_author"
            )
        ]
