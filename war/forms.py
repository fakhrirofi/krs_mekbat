from django import forms
from django.contrib.auth.models import User
from .models import UserData

class RegistrationForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), label="Nama")
    handphone = forms.CharField(widget=forms.TextInput(), label="No. Handphone")
    nim = forms.CharField(widget=forms.TextInput(), label="NIM (Contoh: 112220001)")
    password = forms.CharField(widget=forms.PasswordInput())

    def save(self, commit=True):
        user = User(username=self.cleaned_data['nim'])
        user.set_password(self.cleaned_data['password'])
        data = UserData(user=user)
        data.nim = int(self.cleaned_data['nim'])
        data.name = self.cleaned_data['name']
        data.handphone = self.cleaned_data['handphone']
        if commit:
            user.save()
            data.save()
        return user