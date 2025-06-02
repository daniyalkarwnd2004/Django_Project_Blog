from django import forms
from .models import *


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ("انتقاد", "انتقاد"),
        ("پیشنهاد", "پیشنهاد"),
        ("گزارش", "گزارش"),
    )
    massage = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField(max_length=250, required=True)
    phone = forms.CharField(max_length=11, required=True)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, required=True)

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if phone:
            if phone.isnumeric():
                if phone.startswith("09"):
                    return phone
                else:
                    raise forms.ValidationError("اول شماره تلفن اشتباه است!")
            else:
                raise forms.ValidationError("شماره تلفن عددی نیست!")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "body"]


# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['title', 'description', 'slug', 'publish', 'status', 'reading_time']


class PostUser(forms.Form):
    class Status:
        DRAFT = 'DR'
        PUBLISHED = 'PU'
        REJECTED = 'RJ'
        CHOICES = [
            (DRAFT, 'Draft'),
            (PUBLISHED, 'Published'),
            (REJECTED, 'Rejected'),
        ]

    title = forms.CharField(max_length=250)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    slug = forms.SlugField(max_length=250)
    status = forms.ChoiceField(choices=Status.CHOICES, initial=Status.DRAFT)
    reading_time = forms.IntegerField(min_value=1)

    def clean_title(self):
        title = self.cleaned_data["title"]
        if title:
            if len(title) <= 250:
                return title
            else:
                raise forms.ValidationError("Title must be less than 250 characters.")

    def clean_reading_time(self):
        reading_time = self.cleaned_data["reading_time"]
        if reading_time:
            if reading_time >= 1:
                return reading_time
            else:
                raise forms.ValidationError("Study time must be greater than 0.")


class SearchPost(forms.Form):
    query = forms.CharField()


class CreatedPost(forms.ModelForm):
    image1 = forms.ImageField(required=False, label="image1")
    image2 = forms.ImageField(required=False, label="image2")

    class Meta:
        model = Post
        fields = ["title", "description", "reading_time"]


class LoginForm(forms.Form):
    username = forms.CharField(max_length=250, required=True)
    password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, label="password")
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput, label="repeat password")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['bio', 'birth', 'photo', 'job']

