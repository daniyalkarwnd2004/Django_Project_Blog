from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .forms import PasswordResetRequestForm, SetNewPasswordForm
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator as token_generator
import random

token_generator = PasswordResetTokenGenerator()


def index(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).all()
    posts_random = random.choice(posts)
    return render(request, 'blog/home_page.html', {'posts_top': posts_random})


# def post_list(request, category=None):
#     if category is not None:
#         posts = Post.objects.filter(category = category)
#     else:
#         posts = Post.objects.filter(status=Post.Status.PUBLISHED).all()
#     paginator = Paginator(posts, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     context = {
#         'category': category,
#         'posts': posts
#     }
#     return render(request, "blog/listPost.html", context)


class PostListView(ListView):
    queryset = Post.objects.filter(status=Post.Status.PUBLISHED)
    paginate_by = 6
    context_object_name = 'Posts'
    template_name = "blog/listPost.html"


def post_detail(request, id):
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    form = CommentForm()
    comment = post.comments.filter(activ=True)
    context = {
        "post": post,
        "form": form,
        "comment": comment
    }
    return render(request, "blog/postdetail.html", context)


def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            ticket_obj = Ticket.objects.create()
            ticket_obj.massage = cd["massage"]
            ticket_obj.name = cd["name"]
            ticket_obj.email = cd["email"]
            ticket_obj.phone = cd["phone"]
            ticket_obj.subject = cd["subject"]
            ticket_obj.save()
            return redirect("blog:ticket")
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


@require_POST
def comment_post(request, id_post):
    post = get_object_or_404(Post, id=id_post, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        "post": post,
        "form": form,
        "comment": comment
    }
    return render(request, "forms/comment.html", context)


def post_user(request):
    default_user = User.objects.get(id=1)
    if request.method == "POST":
        form = PostUser(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            add_post = Post.objects.create(
                author=default_user,
                title=cd["title"],
                description=cd["description"],
                slug=cd["slug"],
                status=cd["status"],
                reading_time=cd["reading_time"]
            )
            add_post.save()
            return redirect("blog:index")
    else:
        form = PostUser()
        return render(request, "forms/user_post.html", {"form": form})


def search_post(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchPost(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results1 = Post.objects.filter(status=Post.Status.PUBLISHED) \
                .annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1)
            results2 = Post.objects.filter(status=Post.Status.PUBLISHED) \
                .annotate(similarity=TrigramSimilarity('description', query)).filter(similarity__gt=0.1)
            results3 = Image.objects.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1)
            results4 = Image.objects.annotate(similarity=TrigramSimilarity('description', query)).filter(
                similarity__gt=0.1)
            results = (results1 | results2).order_by('-similarity')
            results_image = (results3 | results4).order_by('-similarity')

    context = {
        'query': query,
        'results': results,
        'results_image': results_image
    }
    return render(request, "blog/search_post.html", context)


@login_required
def profile(request):
    user = request.user
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).filter(author=user)
    context = {
        'user': user,
        'posts': posts
    }
    return render(request, "blog/profile.html", context)


def add_post(request):
    if request.method == "POST":
        form = CreatedPost(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_field=form.cleaned_data["image1"], post=post)
            Image.objects.create(image_field=form.cleaned_data["image2"], post=post)
            post.save()
            return redirect('blog:profile')
    else:
        form = CreatedPost()
    return render(request, "forms/created_post.html", {"form": form})


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile')
    else:
        return render(request, "forms/post-delete.html", {"post": post})


def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    return redirect("blog:profile")


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CreatedPost(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            image1 = form.cleaned_data.get("image1")
            image2 = form.cleaned_data.get("image2")

            if image1:
                Image.objects.create(image_field=image1, post=post)
            if image2:
                Image.objects.create(image_field=image2, post=post)

            return redirect('blog:profile')
    else:
        form = CreatedPost(instance=post)

    return render(request, "forms/created_post.html", {"form": form, "post": post})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd["username"], password=cd["password"])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('blog:profile')
                else:
                    return HttpResponse("Your account is disabled")
            else:
                return HttpResponse("You are not logged in")
    else:
        form = LoginForm()
    return render(request, "user_information/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect('blog:index')


def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = token_generator.make_token(user)
                reset_path = reverse('blog:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                reset_url = request.build_absolute_uri(reset_path)
                send_mail(
                    'Password Reset',
                    f'Click here to reset your password: {reset_url}',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
            return redirect('blog:password_reset_done')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'partials/password_reset_form.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    validlink = False
    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                return redirect('blog:password_reset_complete')
        else:
            form = SetNewPasswordForm()
        return render(request, 'partials/password_reset_confirm.html', {'form': form, 'validlink': validlink})
    else:
        return render(request, 'partials/password_reset_confirm.html', {'validlink': validlink})


def password_reset_done_view(request):
    return render(request, 'partials/password_reset_done.html')


def password_reset_complete_view(request):
    return render(request, 'partials/password_reset_complete.html')


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            Account.objects.create(user=user)
            return render(request, "user_information/congratulations.html", {"user": user})
    else:
        form = UserRegisterForm()
    return render(request, "user_information/register.html", {"form": form})


@login_required
def edit_account(request):
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, instance=request.user.account, files=request.FILES)
        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)
    context = {
        'user_form': user_form,
        'account_form': account_form
    }
    return render(request, 'user_information/edit_information.html', context)


def show_profile(request, username):
    account = get_object_or_404(Account, user__username=username)
    user = account.user
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).filter(author=user)
    context = {
        'user': user,
        'account': account,
        'posts': posts
    }
    return render(request, "user_information/author_profile.html", context)


@login_required
def all_comment(request):
    comment = Comment.objects.filter(post__author=request.user).select_related('post').order_by('-created')
    return render(request, 'forms/all_comments.html', {'comment': comment})


class PostRandom(ListView):
    queryset = Post.objects.filter(status=Post.Status.PUBLISHED)
    paginate_by = 6
    context_object_name = 'Posts'
    template_name = "blog/profile.html"