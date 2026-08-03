from django import forms
from django.contrib.auth import get_user_model

from aide.models import Beneficiaire

User = get_user_model()


class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmer le mot de passe", widget=forms.PasswordInput
    )
    role = forms.ChoiceField(
        choices=[
            (User.Role.DONATEUR, "Donateur"),
            (User.Role.BENEFICIAIRE, "Bénéficiaire"),
        ]
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if user.role == User.Role.BENEFICIAIRE:
                Beneficiaire.objects.create(user=user)
        return user
