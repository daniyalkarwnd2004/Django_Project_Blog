from django.contrib import admin
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter
# Register your models here.

# inline


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publish', 'status', 'reading_time']
    ordering = ['publish']
    list_filter = ['author', ('publish', JDateFieldListFilter), 'status']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ['title']}
    list_editable = ['status', 'reading_time']
    inlines = [ImageInline, CommentInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "subject"]
    list_filter = ['subject']


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ["name", "activ", "created"]
    search_fields = ["name", "body"]
    list_editable = ["activ"]
    list_filter = ["activ", "created", "updated"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["title", "created", "post", '__str__']


@admin.register(Account)
class AdminAccount(admin.ModelAdmin):
    list_display = ['user', 'bio', 'birth', 'photo', 'job']
