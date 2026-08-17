from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={"placeholder": "nom@email.com", "autofocus": True}),
    )


class InscriptionForm(forms.ModelForm):
    nom_complet = forms.CharField(label=_("الاسم الكامل"))
    password1 = forms.CharField(label=_("كلمة المرور"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("تأكيد كلمة المرور"), widget=forms.PasswordInput
    )
    role = forms.ChoiceField(
        label=_("أنا أسجّل بصفتي"),
        choices=[
            (User.Role.DONATEUR, _("متبرّع")),
            (User.Role.RESPONSABLE, _("مسؤول")),
        ],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["email"]

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
        nom_complet = self.cleaned_data["nom_complet"].strip()
        prenom, _sep, nom = nom_complet.partition(" ")
        user.first_name = prenom
        user.last_name = nom or prenom
        user.username = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        user.is_active = user.role != User.Role.RESPONSABLE
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
