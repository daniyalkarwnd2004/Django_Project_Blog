from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
from django.urls import path, reverse_lazy

app_name = "blog"
urlpatterns = [
    path('', views.index, name="index"),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<id>', views.post_detail, name='post_title'),
    path('posts/<id_post>/comment', views.comment_post, name='comment_post'),
    path('ticket/', views.ticket, name="ticket"),
    path('postuser/', views.post_user, name='postuser'),
    path('search/', views.search_post, name="search_post"),
    path('profile/', views.profile, name="profile"),
    path('profile/addpost', views.add_post, name="add_post"),
    path('profile/addpost/<post_id>', views.edit_post, name="edit_post"),
    path('profile/delete_post/<post_id>', views.delete_post, name="delete_post"),
    path('profile/delete_image/<image_id>', views.delete_image, name="delete_image"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('password-change/', auth_view.PasswordChangeView.as_view(
        template_name='user_information/password_change_form.html',
        success_url='/blog/password-change/done/'), name='password_change'),
    path('password-change/done/', auth_view.PasswordChangeDoneView.as_view(
        template_name='user_information/password_change_done.html'), name='password_change_done'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete_view, name='password_reset_complete'),
    path('register/', views.register, name="register"),
    path('account/edit/', views.edit_account, name='edit_account'),
    path('user_profile/<str:username>/', views.show_profile, name='user_profile'),
    path('all_comments', views.all_comment, name='all_comments'),
    path('post/', views.PostListView.as_view(), name='post_list'),

]

