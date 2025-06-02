from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django_jalali.db import models as jmodels
from django_resized import ResizedImageField
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
from django.template.defaultfilters import slugify

# Create your models here.


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DR', 'Draft'
        PUBLISHED = 'PU', 'Published'
        REJECTED = 'RJ', 'Rejected'

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts', verbose_name="نویسنده")
    title = models.CharField(max_length=250, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    slug = models.SlugField(max_length=250, verbose_name="اسلاگ")
    publish = jmodels.jDateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name="وضعیت")
    reading_time = models.PositiveIntegerField(verbose_name="زمان مطالعه")
    objects = jmodels.jManager()
    Published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]
        verbose_name = "پست ها"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.title

    def get_absolut_url(self):
        return reverse('blog:post_title', args=[self.id])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Ticket(models.Model):
    massage = models.TextField(verbose_name="پیغام")
    name = models.CharField(max_length=250, verbose_name="نام")
    email = models.EmailField(max_length=250, verbose_name="ایمیل")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    subject = models.CharField(max_length=250, verbose_name="نوع درخواست")
    objects = models.Manager()

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت ها"

    def __str__(self):
        return self.subject


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    name = models.CharField(max_length=250, verbose_name="نام")
    body = models.TextField(verbose_name="متن کامنت")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ بروز رسانی")
    activ = models.BooleanField(default=False, verbose_name="وضعیت")
    objects = models.Manager()

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"])
        ]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

    def __str__(self):
        return self.name


def get_image_upload_to(instance, filename):
    current_year = timezone.now().year
    return f'post_images/{current_year}/{filename}'


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images", verbose_name="پست")
    image_field = ResizedImageField(upload_to=get_image_upload_to, verbose_name="تصویر", size=[500, 500],
                                    crop=['middle', 'center'], quality=75)
    title = models.CharField(max_length=250, verbose_name="عنوان", null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    created = jmodels.jDateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"])
        ]
        verbose_name = "تصویر"
        verbose_name_plural = "تصویر ها"

    def __str__(self):
        if self.title:
            return self.title
        else:
            file_name = os.path.basename(self.image_field.name)
            return file_name


@receiver(post_delete, sender=Image)
def delete_image_file(sender, instance, **kwargs):
    if instance.image_field:
        instance.image_field.delete(save=False)


@receiver(post_delete, sender=Post)
def delete_post_images(sender, instance, **kwargs):
    for image in instance.images.all():
        if image.image_field:
            image.image_field.delete(save=False)


def get_image_upload_to_account(instance, filename):
    current_year = timezone.now().year
    return f'Account/{current_year}/{filename}'


class Account(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    bio = models.TextField(verbose_name="توضیحات", blank=True, null=True)
    birth = jmodels.jDateField(verbose_name="تاریخ تولد", blank=True, null=True)
    photo = ResizedImageField(upload_to=get_image_upload_to_account, verbose_name="تصویر", size=[500, 500], crop=['middle', 'center'], quality=75)
    job = models.CharField(max_length=250, verbose_name="شغل", blank=True, null=True)
    objects = models.Manager()

    class Meta:
        verbose_name = "اکانت"
        verbose_name_plural = "اکانت ها"

    def __str__(self):
        return self.user.username







