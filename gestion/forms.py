from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import UserProfile, OffreStage, Entreprise, Etudiant, ExperienceProfessionnelle, Competence, CV
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import ValidationError

class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError('This user is no longer active.')

    def clean(self):
        return super().clean()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'user_type')

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user_type = self.cleaned_data.get('user_type')
    #     if commit:
    #         user.save()
    #
    #         # Vérifie si un profil utilisateur existe déjà, sinon on le crée
    #         user_profile, created = UserProfile.objects.update_or_create(
    #             user=user, defaults={'user_type': user_type}
    #         )
    #
    #     return user


class OffreStageForm(forms.ModelForm):
    type_stage = forms.ChoiceField(
        choices=OffreStage.TYPE_STAGE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = OffreStage
        fields = ['titre', 'type_stage', 'localisation', 'duree', 'date_limite_postulation', 'description']
        widgets = {
            'date_limite_postulation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Rechercher',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Rechercher une offre...', 'class': 'form-control'}),
    )

class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['logo', 'nom', 'email_contact', 'created', 'siege', 'adresse', 'secteur_activite', 'description']  # Vérifiez ici

class ExperienceProfessionnelleForm(forms.ModelForm):
    class Meta:
        model = ExperienceProfessionnelle
        fields = ['poste', 'entreprise', 'departement', 'date_debut', 'date_fin', 'siege_entreprise', 'pays_entreprise']

class UploadCVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['fichier']
        widgets = {
            'fichier': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
            }),
        }


class CompetenceForm(forms.ModelForm):
    class Meta:
        model = Competence
        fields = ['nom', 'niveau', 'date_acquisition', 'description']

class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['photo', 'date_de_naissance', 'adresse', 'telephone']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class LettreMotivationForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['lettre_motivation']


