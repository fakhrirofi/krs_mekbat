from django import forms
from django.contrib.auth.models import User
from .models import UserData

class RegistrationForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), label="Nama")
    handphone = forms.CharField(widget=forms.TextInput(), label="No. Handphone")
    nim = forms.IntegerField(widget=forms.TextInput(), label="NIM (Contoh: 112220001)")
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Konfirmasi Password")

    def clean_nim(self):
        nim = self.cleaned_data.get('nim')
        if not str(nim).isnumeric():
             raise forms.ValidationError("NIM harus berupa angka.")
        return nim

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password minimal 8 karakter.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Password tidak cocok.")
            
        return cleaned_data

    def save(self, commit=True):
        user = User(username=self.cleaned_data['nim'])
        user.set_password(self.cleaned_data['password'])
        data = UserData(user=user)
        data.nim = int(self.cleaned_data['nim'])
        data.name = self.cleaned_data['name']
        user.first_name = self.cleaned_data['name']
        data.handphone = self.cleaned_data['handphone']
        if commit:
            user.save()
            data.save()
        return user