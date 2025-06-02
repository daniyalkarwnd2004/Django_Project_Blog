from ..models import Post, Comment
from django.db.models import Count
from markdown import markdown
from django.db.models import Min, Max
from django.utils.safestring import mark_safe
from django import template
from django.contrib.auth.models import User
from blog.models import models

register = template.Library()


@register.simple_tag()
def title_post():
    return Post.objects.filter(status=Post.Status.PUBLISHED).count()


@register.simple_tag()
def title_comment():
    return Comment.objects.filter(activ=True).count()


@register.simple_tag()
def last_post():
    return Post.objects.filter(status=Post.Status.PUBLISHED).last().publish


@register.simple_tag()
def active_user():
    user = User.objects.annotate(post_count=Count("user_posts")).order_by("-post_count").first
    return user


@register.simple_tag()
def top_post(count=3):
    return Post.objects.filter(status=Post.Status.PUBLISHED).annotate(comment_count=Count("comments")). \
               order_by('-comment_count')[:count]


@register.simple_tag()
def min_reading_time():
    result = Post.objects.filter(status=Post.Status.PUBLISHED).aggregate(min_time=Min("reading_time"))
    return result.get("min_time", 0)


@register.simple_tag()
def max_reading_time():
    result = Post.objects.filter(status=Post.Status.PUBLISHED).aggregate(max_time=Max('reading_time'))
    return result.get("max_time", 0)


@register.inclusion_tag("partials/last_post.html")
def list_post(count=5):
    l_post = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-publish")[:count]
    context = {
        "l_post": l_post
    }
    return context


@register.inclusion_tag("partials/active_user_post.html")
def active_user(count=3):
    user_active = User.objects.annotate(post_count=Count("user_posts")).first()
    posts = Post.objects.filter(author=user_active)[:count]
    return {
        "user_active": user_active,
        "latest_posts": posts
    }


@register.filter("markdown")
def text_markdown(text):
    return mark_safe(markdown(text))


@register.filter(name="sensor")
def text_sensor(text):
    list_filter = ["donkey", "animal", "fool", "idiot", "you are a fool", "stupid person"]

    def sensor(text, list_filter):
        for phrase in list_filter:
            text = text.replace(phrase, "*" * len(phrase))
        return text

    return sensor(text, list_filter)
