from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# Modèle User avec un champ user_type pour distinguer les types d'utilisateurs
class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('student', 'Etudiant'),
        ('recruiter', 'Recruteur'),
        ('service_stage', 'Service Stage'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if not self.user_type:
            raise ValueError("Le type d'utilisateur doit être spécifié.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


# Modèle pour les entreprises (recruteurs)
class Entreprise(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # Permet d'ajouter temporairement des valeurs nulles
        blank=True,  # Autorise le champ vide dans les formulaires
    )
    logo = models.ImageField(upload_to='logos/', default='logos/default_logo.png', blank=True, null=True)
    nom = models.CharField(max_length=200)
    created = models.DateField(blank=True, null=True)
    siege = models.CharField(max_length=200, blank=True, null=True)
    adresse = models.CharField(max_length=300, blank=True)
    description = RichTextField(blank=True)
    secteur_activite = models.CharField(max_length=300, blank=True)
    email_contact = models.EmailField(blank=True)

    def __str__(self):
        return self.nom

def validate_pdf(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError("Seuls les fichiers PDF sont autorisés.")

# Modèle pour les étudiants
class Etudiant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # Permet d'ajouter temporairement des valeurs nulles
        blank=True,  # Autorise le champ vide dans les formulaires
        related_name='etudiant',
    )
    photo = models.ImageField(upload_to='media/photos', blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True)
    date_de_naissance = models.DateField(null=True, blank=True)
    adresse = models.CharField(max_length=200, null=True, blank=True)
    # Nouveaux champs pour les documents
    lettre_motivation = models.FileField(upload_to='etudiants/lettres_motivation/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class CV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cv')
    fichier = models.FileField(upload_to='etudiants/cv/', blank=True, null=True)
    date_upload = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.fichier.name}"


# Informations académiques
class Formation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="formations")
    titre = models.CharField(max_length=100, blank=True, null=True)
    diplome = models.CharField(max_length=200, blank=True)
    etablissement = models.CharField(max_length=255, blank=True)
    siege_etablissement = models.CharField(max_length=255, blank=True)
    pays_etablissement = models.CharField(max_length=255, blank=True)
    date_inscription = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.titre

class Competence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="competences")
    nom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=50, choices=[("Débutant", "Débutant"),
                                                      ("Intermédiaire", "Intermédiaire"),
                                                      ("Avancé", "Avancé"),
                                                      ("Expert", "Expert")])
    date_acquisition = models.DateField(null=True, blank=True)  # Si tu veux suivre la date d'acquisition
    description = RichTextField(blank=True, null=True)  # Une petite description optionnelle

    def __str__(self):
        return f"{self.nom} ({self.niveau})"


class ExperienceProfessionnelle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="experiences_professionnelles")
    poste = models.CharField(max_length=100)
    entreprise = models.CharField(max_length=150)
    departement = models.CharField(max_length=255, null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    siege_entreprise = models.CharField(max_length=255, blank=True)
    pays_entreprise = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.poste} ({self.entreprise})"

class Entretien(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entretiens")
    entreprise = models.CharField(max_length=150)
    date = models.DateField()
    statut = models.CharField(max_length=50, choices=[("Prévu", "Prévu"), ("Passé", "Passé"), ("Annulé", "Annulé")])

    def __str__(self):
        return f"{self.entreprise} - {self.statut}"



class ServiceStage(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # Permet d'ajouter temporairement des valeurs nulles
        blank=True,  # Autorise le champ vide dans les formulaires
    )
    responsable = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Service Stage - {self.user}"

# Modèle pour les offres de stage
class OffreStage(models.Model):
    TYPE_STAGE_CHOICES = (
        ('plein', 'Temps plein'),
        ('partiel', 'Temps partiel'),
    )
    titre = models.CharField(max_length=200)
    description = RichTextField()
    type_stage = models.CharField(max_length=200, choices=TYPE_STAGE_CHOICES)
    localisation = models.CharField(max_length=200)
    duree = models.IntegerField()
    date_publication = models.DateTimeField(auto_now_add=True)
    date_limite_postulation = models.DateField()
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre

class Candidature(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('selectionne', 'Accepté'),
        ('rejete', 'Rejeté'),
    ]
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    offre = models.ForeignKey(OffreStage, on_delete=models.CASCADE, related_name="candidatures")
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, blank=True)
    lettre_motivation = models.FileField(upload_to='lettres_motivation/', blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    commentaires = models.TextField(null=True, blank=True)
    date_soumission = models.DateField(auto_now_add=True)
    date_reponse = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.etudiant.username} - {self.offre.titre}'



class Contrat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contrats", null=True, blank=True)
    type_contrat = models.CharField(max_length=200)
    poste = models.CharField(max_length=100, null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entreprise} - {self.poste}"




# Signal pour créer le profil en fonction du type d'utilisateur
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         # Créer un profil générique pour chaque utilisateur
#         user_profile = UserProfile.objects.create(user=instance)
#         # Créer des profils spécifiques selon le type d'utilisateur
#         if user_profile.user_type =='student':
#             Etudiant.objects.create(user=instance)
#         elif user_profile.user_type =='recruiter':
#             Entreprise.objects.create(user=instance)
#         elif user_profile.user_type =='service_stage':
#             ServiceStage.objects.create(user=instance)
#
#
#
# # Signal pour sauvegarder le profil après la création ou modification de l'utilisateur
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     try:
#         instance.profile.save()
#     except UserProfile.DoesNotExist:
#         # Si le profil n'existe pas, on peut créer un profil par défaut ou prendre une autre action.
#         user_profile = UserProfile.objects.create(user=instance)
#         user_profile.save()



