from django.core.exceptions import ValidationError

__author__ = 'justin'
from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=32)
    email = forms.EmailField()
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    repeat_password = forms.CharField(max_length=32, widget=forms.PasswordInput)

    def clean_username(self):
        try:
            username = self.cleaned_data['username']
            User.objects.get(username=username)
            raise ValidationError("Username already exists. Please choose another.")
        except User.DoesNotExist:
            return username

    def clean_password(self):
        pw1 = self.cleaned_data['password']
        pw2 = self.cleaned_data['repeat_password']
        if pw1 != pwd2:
            raise ValidationError("Passwords do not match.")
        return pw1

