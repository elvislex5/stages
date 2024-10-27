from django.contrib import admin
from .models import Entreprise, Etudiant, ServiceStage, Contrat, Candidature, OffreStage

# Register your models here.

admin.site.register(Entreprise)
admin.site.register(Etudiant)
admin.site.register(ServiceStage)
admin.site.register(Candidature)
admin.site.register(OffreStage)
admin.site.register(Contrat)
