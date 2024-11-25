from django.contrib import admin
from .models import Entreprise, Etudiant, ServiceStage, Contrat, Candidature, OffreStage, UserProfile, Formation, ExperienceProfessionnelle, Competence, Entretien, CV

# Register your models here.

admin.site.register(Entreprise)
admin.site.register(Etudiant)
admin.site.register(ServiceStage)
admin.site.register(Candidature)
admin.site.register(OffreStage)
admin.site.register(Contrat)
admin.site.register(UserProfile)
admin.site.register(Formation)
admin.site.register(ExperienceProfessionnelle)
admin.site.register(Competence)
admin.site.register(Entretien)
admin.site.register(CV)
