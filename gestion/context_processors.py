from .models import Candidature

def candidatures_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'etudiant'):
        # Compter les candidatures pour l'étudiant connecté
        return {
            'candidatures_count': Candidature.objects.filter(etudiant=request.user).count()
        }
    return {'candidatures_count': 0}
