from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

from .models import OffreStage, Candidature, Contrat
from .forms import AuthenticationForm, SignUpForm


# Create your views here.

def accueil(request):
    return render(request, 'base.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('consulter_offres')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) #Auto connexion après l'inscription
            return redirect('consulter_offres')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def consulter_offres(request):
    offres = OffreStage.objects.all()
    return render(request, 'offres/consulter_offres.html', {'offres': offres})

@login_required
def postuler_offre(request, offre_id):
    offre = get_object_or_404(OffreStage, pk=offre_id)

    # Vérifier que l'étudiant ait déjà postulé à cette offre
    if Candidature.objects.filter(etudiant=request.user.etudiant, stage=offre).exists():
        return render(request, 'offres/deja_postule.html')

    # Créer une nouvelle candidature
    candidature = Candidature.objects.create(etudiant=request.user.etudiant, stage=offre, etat='En attente')
    candidature.save()

    return redirect('consulter_offres')

@login_required
def suivre_candidatures(request):
    candidatures = Candidature.objects.filter(etudiant=request.user.etudiant)
    return render(request, 'candidatures/suivre_candidatures.html', {"candidatures": candidatures})

@login_required
def gerer_contrats(request):
    contrats = Contrat.objects.filter(entreprise=request.user.entreprise)
    return render(request, 'contrats/gerer_contrats.html', {"contrats": contrats})

