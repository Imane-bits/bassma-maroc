from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Mot de passe"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"), widget=forms.PasswordInput
    )
    role = forms.ChoiceField(
        label=_("rôle"),
        choices=[
            (User.Role.DONATEUR, User.Role.DONATEUR.label),
            (User.Role.RESPONSABLE, _("Gestionnaire")),
        ],
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Un compte existe déjà avec cet email."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        user.is_active = user.role != User.Role.RESPONSABLE
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
