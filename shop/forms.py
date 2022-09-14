from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class RegistrationFrom(forms.Form):
    username = forms.CharField(
        label="Tên Đăng Nhập",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mật Khẩu",
        max_length=20,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label="Xác Nhận Lại Mật Khẩu",
        max_length=20,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label="Tên",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Họ",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.CharField(
        label="Email",
        max_length=70,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
            raise ValidationError(f'Tên đăng nhập {username} đã tồn tại')
        except User.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
            raise ValidationError(f'Email {email} đã trùng')
        except User.DoesNotExist:
            return email

    def clean_confirm_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError("mật khẩu nhập lại không giống")
        return self.cleaned_data['confirm_password']

    def save(self):
        User.objects.create_user(
            username = self.cleaned_data['username'],
            password = self.cleaned_data['password'],
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            email = self.cleaned_data['email'],
    )

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Tên Đăng Nhập",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mật Khẩu",
        max_length=20,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
