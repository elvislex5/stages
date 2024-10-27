from django.db import models

# Create your models here.

class Entreprise(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    secteur_activite = models.CharField(max_length=300, blank=True)
    email_contact = models.EmailField(blank=True)

    def __str__(self):
        return self.nom

class Etudiant(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    matricule = models.CharField(max_length=200, blank=True)
    niveau = models.CharField(max_length=200, blank=True)
    filiere = models.CharField(max_length=200, blank=True)
    cv = models.FileField(upload_to='media/cv', blank=True)

    def __str__(self):
        return self.user.username


class ServiceStage(models.Model):
    responsable = models.CharField(max_length=200, blank=True)


class OffreStage(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type_stage = models.CharField(max_length=200, choices=[('TEMPS PLEIN', 'Temps plein'), ('PARTIEL', 'partiel')])
    localisation = models.CharField(max_length=200)
    duree = models.IntegerField()
    date_publication = models.DateField(auto_now_add=True)
    date_limite_postulation = models.DateField()
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceStage, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre

class Candidature(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    stage = models.ForeignKey(OffreStage, on_delete=models.CASCADE)
    date_soumission = models.DateField(auto_now_add=True)
    etat = models.CharField(max_length=200, choices=[('EN ATTENTE', 'En attente'), ('ACCEPTE', 'Accepté'), ('REFUSE','Refusé')])
    date_reponse = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.etudiant.user.username} - {self.stage.titre}'

class Contrat(models.Model):
    type_contrat = models.CharField(max_length=200)
    date_debut = models.DateField()
    date_fin = models.DateField()
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

    def __str__(self):
        return f'Contrat - {self.etudiant.user.username} - {self.entreprise.nom}'




