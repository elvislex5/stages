from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
# Librairie pour la barre de recherche
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramSimilarity, SearchRank
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView, TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import CustomLoginForm, SignUpForm, OffreStageForm, SearchForm, EntrepriseForm, EtudiantForm, UserForm, \
    ExperienceProfessionnelleForm, CompetenceForm, UploadCVForm, LettreMotivationForm
from .models import OffreStage, Candidature, Contrat, Etudiant, Entreprise, ServiceStage, UserProfile, Formation, \
    ExperienceProfessionnelle, Competence, CV


# Create your views here.

def is_recruteur(user):
    return user.user_type == 'recruiter'

class HomeView(TemplateView):
    template_name = 'accueil/home.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         user_profile = getattr(request.user, 'profile', None)
    #         if user_profile:
    #             if user_profile.user_type == 'student':
    #                 return redirect('espace_etudiant')
    #             elif user_profile.user_type == 'recruiter':
    #                 return redirect('espace_recruteur')
    #             elif user_profile.user_type == 'service_stage':
    #                 return redirect('espace_service_stage')
    #         return redirect('accueil')  # Par défaut
    #     return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect.")
        return super().form_invalid(form)

    def get_success_url(self):
        # Vérifier le type d'utilisateur via le profil
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile:
            if user_profile.user_type == 'student':
                return reverse_lazy('espace_etudiant')
            elif user_profile.user_type == 'recruiter':
                return reverse_lazy('espace_recruteur')
            elif user_profile.user_type == 'service_stage':
                return reverse_lazy('espace_service_stage')
        # Redirection par défaut si aucun type valide
        return reverse_lazy('accueil')

    def dispatch(self, request, *args, **kwargs):
        # Rediriger les utilisateurs déjà connectés vers leur espace approprié
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_profile = getattr(request.user, 'profile', None)
            if user_profile:
                if user_profile.user_type == 'student':
                    return redirect('espace_etudiant')
                elif user_profile.user_type == 'recruiter':
                    return redirect('espace_recruteur')
                elif user_profile.user_type == 'service_stage':
                    return redirect('espace_service_stage')
            return redirect('accueil')  # Par défaut
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data.get('user_type')

            # Vérifiez si un profil existe déjà pour cet utilisateur
            user_profile, created = UserProfile.objects.get_or_create(user=user, defaults={'user_type': user_type})

            if created:  # Profil nouvellement créé
                # Créer le profil spécifique selon le type d'utilisateur
                if user_type == 'student':
                    Etudiant.objects.create(user=user)
                    success_url = reverse_lazy('espace_etudiant')
                elif user_type == 'recruiter':
                    success_url = reverse_lazy('creer_entreprise')
                elif user_type == 'service_stage':
                    ServiceStage.objects.create(user=user)
                    success_url = reverse_lazy('espace_service_stage')
                else:
                    success_url = reverse_lazy('accueil')  # Par défaut si user_type non spécifié
            else:
                # Si le profil existe déjà, rediriger directement vers la page d'accueil
                success_url = reverse_lazy('accueil')

            # Connexion de l'utilisateur
            login(request, user)
            return redirect(success_url)

        # En cas de formulaire invalide, rester sur la page d'inscription
        return render(request, self.template_name, {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accueil')

# # Profil de l'étudiant
# class StudentProfileView(LoginRequiredMixin, TemplateView):
#     template_name = 'etudiant/profil.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         etudiant = Etudiant.objects.get(user=self.request.user)
#         context['etudiant'] = etudiant
#         return context


# Vue pour l'espace étudiant
class EspaceEtudiantView(LoginRequiredMixin, TemplateView):
    template_name = 'etudiant/profil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            etudiant = Etudiant.objects.get(user=self.request.user)
        except Etudiant.DoesNotExist:
            # Rediriger ou afficher un message d'erreur si l'étudiant n'existe pas
            return redirect('page_non_autorisee')

        # Ajouter les autres données pertinentes à afficher dans le contexte
        context['etudiant'] = etudiant  # Par exemple, vous pouvez ajouter les informations de l'étudiant ici

        return context

class ProfilEtudiantDetailView(LoginRequiredMixin, View):
    template_name = 'etudiant/profil_etudiant_detail.html'

    def get(self, request, *args, **kwargs):
        etudiant = request.user.etudiant
        user = request.user
        etudiant_form = EtudiantForm(instance=etudiant)
        user_form = UserForm(instance=user)
        return render(request, self.template_name, {
            'etudiant_form': etudiant_form,
            'user_form': user_form,
            'etudiant': etudiant,
        })

    def post(self, request, *args, **kwargs):
        etudiant = request.user.etudiant
        user = request.user
        etudiant_form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
        user_form = UserForm(request.POST, instance=user)

        if etudiant_form.is_valid() and user_form.is_valid():
            etudiant_form.save()
            user_form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès !")
            return HttpResponseRedirect(reverse('profil_etudiant'))  # Redirige après la sauvegarde
        return render(request, self.template_name, {
            'etudiant_form': etudiant_form,
            'user_form': user_form,
            'etudiant': etudiant,
        })

class FormationListView(LoginRequiredMixin, ListView):
    model = Formation
    template_name = 'etudiant/formations_list.html'
    context_object_name = 'formations'

    def get_queryset(self):
        # Récupérer uniquement les formations de l'utilisateur connecté
        return Formation.objects.filter(user=self.request.user)

class FormationCreateView(LoginRequiredMixin, CreateView):
    model = Formation
    template_name = 'etudiant/formation_form.html'
    fields = ['titre', 'diplome', 'etablissement', 'siege_etablissement', 'pays_etablissement', 'date_inscription', 'date_fin']
    success_url = reverse_lazy('formations_list')

    def form_valid(self, form):
        # Associer automatiquement l'utilisateur connecté à la formation
        form.instance.user = self.request.user
        return super().form_valid(form)

class FormationUpdateView(LoginRequiredMixin, UpdateView):
    model = Formation
    template_name = 'etudiant/formation_form.html'
    fields = ['titre', 'diplome', 'etablissement', 'siege_etablissement', 'pays_etablissement', 'date_inscription', 'date_fin']
    success_url = reverse_lazy('formations_list')

    def get_queryset(self):
        # Limiter l'accès aux formations appartenant uniquement à l'utilisateur connecté
        return Formation.objects.filter(user=self.request.user)

class FormationDeleteView(LoginRequiredMixin, DeleteView):
    model = Formation
    template_name = 'etudiant/formation_confirm_delete.html'
    context_object_name = 'formation'
    success_url = reverse_lazy('formations_list')

    def get_queryset(self):
        # Limiter l'accès aux formations appartenant uniquement à l'utilisateur connecté
        return Formation.objects.filter(user=self.request.user)


class ExperienceProfessionnelleListView(LoginRequiredMixin, ListView):
    model = ExperienceProfessionnelle
    template_name = 'etudiant/experiences_professionnelles_list.html'
    context_object_name = 'experiences'

    def get_queryset(self):
        # Limiter l'accès aux expériences professionnelles de l'utilisateur connecté
        return ExperienceProfessionnelle.objects.filter(user=self.request.user)

class ExperienceProfessionnelleCreateView(LoginRequiredMixin, CreateView):
    model = ExperienceProfessionnelle
    form_class = ExperienceProfessionnelleForm
    template_name = 'etudiant/experience_form.html'
    success_url = reverse_lazy('experiences_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associer l'utilisateur connecté à l'expérience
        return super().form_valid(form)

class ExperienceProfessionnelleUpdateView(LoginRequiredMixin, UpdateView):
    model = ExperienceProfessionnelle
    form_class = ExperienceProfessionnelleForm
    template_name = 'etudiant/experience_form.html'
    success_url = reverse_lazy('experiences_list')

    def get_queryset(self):
        # Limiter l'accès aux expériences professionnelles de l'utilisateur connecté
        return ExperienceProfessionnelle.objects.filter(user=self.request.user)

class ExperienceProfessionnelleDeleteView(LoginRequiredMixin, DeleteView):
    model = ExperienceProfessionnelle
    template_name = 'etudiant/experience_confirm_delete.html'
    context_object_name = 'experience'
    success_url = reverse_lazy('experiences_list')

    def get_queryset(self):
        # Limiter l'accès aux expériences professionnelles de l'utilisateur connecté
        return ExperienceProfessionnelle.objects.filter(user=self.request.user)

class DocumentOptionsView(TemplateView):
    template_name = 'etudiant/document_options.html'

class CVDetailView(LoginRequiredMixin, DetailView):
    model = CV
    template_name = 'etudiant/cv_detail.html'

    def get_object(self):
        try:
            # Récupérer le CV lié à l'utilisateur
            return CV.objects.get(user=self.request.user)
        except CV.DoesNotExist:
            # Redirigez l'utilisateur vers la page d'ajout de CV
            return redirect('cv_upload')

class CVUploadView(FormView):
    template_name = "etudiant/upload_cv.html"
    form_class = UploadCVForm

    def form_valid(self, form):
        # Récupérer l'utilisateur connecté
        user = self.request.user
        # Vérifier s'il a déjà un CV
        cv, created = CV.objects.get_or_create(user=user)
        cv.fichier = form.cleaned_data['fichier']
        cv.save()
        return redirect('cv_detail')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class CVGenerateView(TemplateView):
    template_name = 'etudiant/cv_template.html'

    def get_context_data(self, **kwargs):
        # Récupération des informations de l'utilisateur connecté
        user = self.request.user
        # Si vous utilisez un modèle "Etudiant"
        etudiant = getattr(user, 'etudiant', None)
        formations = Formation.objects.filter(user=user)
        experiences = ExperienceProfessionnelle.objects.filter(user=user)
        competences = Competence.objects.filter(user=user)

        context = super().get_context_data(**kwargs)
        context.update({
            'user': user,
            'etudiant': etudiant,
            'formations': formations,
            'experiences': experiences,
            'competences': competences,
        })
        return context

class CVGeneratePDFView(View):
    def get(self, request, *args, **kwargs):
        # Récupération des informations de l'utilisateur connecté
        user = request.user
        formations = Formation.objects.filter(user=user)
        experiences = ExperienceProfessionnelle.objects.filter(user=user)
        competences = Competence.objects.filter(user=user)

        # Création de la réponse pour envoyer le PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="CV.pdf"'

        # Création du PDF avec ReportLab
        c = canvas.Canvas(response, pagesize=letter)

        # Définition des marges et du positionnement
        width, height = letter
        margin_left = 50
        margin_top = height - 50
        line_height = 14

        # Ajouter un titre (nom de l'utilisateur)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin_left, margin_top, f"{user.first_name} {user.last_name}")

        # Positionnement pour les sections suivantes
        y_position = margin_top - 40

        # Ajouter les formations
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_left, y_position, "Formations:")
        y_position -= line_height

        c.setFont("Helvetica", 10)
        for formation in formations:
            c.drawString(margin_left, y_position, f"{formation.titre} - {formation.date_fin}")
            y_position -= line_height

        # Ajouter les expériences professionnelles
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_left, y_position, "Expériences professionnelles:")
        y_position -= line_height

        c.setFont("Helvetica", 10)
        for experience in experiences:
            c.drawString(margin_left, y_position, f"{experience.poste} - {experience.entreprise}")
            y_position -= line_height

        # Ajouter les compétences
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_left, y_position, "Compétences:")
        y_position -= line_height

        c.setFont("Helvetica", 10)
        for competence in competences:
            c.drawString(margin_left, y_position, competence.nom)
            y_position -= line_height

        # Enregistrer le fichier PDF
        c.showPage()
        c.save()

        return response

class CVDeleteView(View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        cv = get_object_or_404(CV, user=user)
        cv.fichier.delete()
        cv.delete()
        return redirect('cv_upload')

# class LettreMotivationDetailView(TemplateView):
#     template_name = "etudiant/lettre_motivation_detail.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Récupérer l'étudiant connecté
#         etudiant = get_object_or_404(Etudiant, user=self.request.user)
#         context['lettre_motivation'] = etudiant.lettre_motivation  # Champ lettre_motivation du modèle Etudiant
#         return context
#
# class LettreMotivationUpdateView(UpdateView):
#     model = Etudiant
#     form_class = LettreMotivationForm
#     template_name = 'etudiant/upload_lettre_motivation.html'
#     success_url = reverse_lazy('lettre_motivation_detail')  # Vous pouvez rediriger vers une page de confirmation
#
#     def get_object(self, queryset=None):
#         # Retourne l'étudiant actuellement connecté
#         return self.request.user.etudiant  # Assurez-vous que le modèle Etudiant est lié à l'utilisateur


class CompetenceListView(LoginRequiredMixin, ListView):
    model = Competence
    template_name = 'etudiant/competences_list.html'
    context_object_name = 'competences'

    def get_queryset(self):
        # Limiter l'accès aux compétences de l'utilisateur connecté
        return Competence.objects.filter(user=self.request.user)

class CompetenceCreateView(LoginRequiredMixin, CreateView):
    model = Competence
    form_class = CompetenceForm
    template_name = 'etudiant/competence_form.html'
    success_url = reverse_lazy('competences_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associer l'utilisateur connecté à la compétence
        return super().form_valid(form)

class CompetenceUpdateView(LoginRequiredMixin, UpdateView):
    model = Competence
    form_class = CompetenceForm
    template_name = 'etudiant/competence_form.html'
    success_url = reverse_lazy('competences_list')

    def get_queryset(self):
        # Limiter l'accès aux compétences de l'utilisateur connecté
        return Competence.objects.filter(user=self.request.user)

class CompetenceDeleteView(LoginRequiredMixin, DeleteView):
    model = Competence
    template_name = 'etudiant/competence_confirm_delete.html'
    context_object_name = 'competence'
    success_url = reverse_lazy('competences_list')

    def get_queryset(self):
        # Limiter l'accès aux compétences de l'utilisateur connecté
        return Competence.objects.filter(user=self.request.user)

class EspaceRecruteurView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = OffreStage
    template_name = 'recruteur/accueil.html'
    context_object_name = 'offres'

    def get_queryset(self):
        return OffreStage.objects.filter(entreprise=self.request.user.entreprise)

    def test_func(self):
        # Vérifie si l'utilisateur est un recruteur
        return hasattr(self.request.user, 'entreprise')

    def handle_no_permission(self):
        # Redirige vers une page d'erreur ou d'accueil si non autorisé
        return redirect('accueil')

class OffresRecruteurListView(LoginRequiredMixin, ListView):
    model = OffreStage
    template_name = 'recruteur/mes_offres.html'
    context_object_name = 'offres'

    def get_queryset(self):
        # Affiche uniquement les offres de l'entreprise du recruteur
        queryset = OffreStage.objects.filter(entreprise=self.request.user.entreprise)
        return queryset

class OffreDetailRecruteurView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = OffreStage
    template_name = 'recruteur/offre_detail_recruteur.html'
    context_object_name = 'offre'

    def test_func(self):
        # Vérifie si l'utilisateur est un recruteur et l'auteur de l'offre
        return self.request.user.profile.user_type == 'recruiter' and self.get_object().entreprise == self.request.user.entreprise

class EntrepriseRecruteurDetailView(LoginRequiredMixin, DetailView):
    model = Entreprise
    template_name = 'recruteur/entreprise_recruteur_detail.html'

    def get_object(self, queryset=None):
        # Obtenez l'entreprise associée à l'utilisateur
        entreprise = Entreprise.objects.filter(user=self.request.user).first()
        if not entreprise:
            # Si aucune entreprise n'est associée, redirigez vers la création d'entreprise
            messages.warning(self.request, "Vous devez d'abord créer une entreprise.")
            return redirect('creer_entreprise')  # Assurez-vous que cette vue est configurée
        return entreprise

class EntrepriseListView(ListView):
    model = Entreprise
    template_name = 'entreprise/entreprise_list.html'
    context_object_name = 'entreprises'

    def get_queryset(self):
        return Entreprise.objects.all()

class EntrepriseDetailView(DetailView):
    model = Entreprise
    template_name = 'entreprise/entreprise_detail.html'
    context_object_name = 'entreprise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entreprise = self.get_object()
        context['offres'] = OffreStage.objects.filter(entreprise=entreprise)
        return context

class CandidaturesReçuesListView(LoginRequiredMixin, ListView):
    model = Candidature
    template_name = 'recruteur/candidatures_recues.html'
    context_object_name = 'candidatures'

    def get_queryset(self):
        return Candidature.objects.filter(offre__entreprise=self.request.user.entreprise)

    def post(self, request, *args, **kwargs):
        # Mettre à jour le statut d'une candidature
        candidature_id = request.POST.get('candidature_id')
        statut = request.POST.get('statut')
        try:
            candidature = Candidature.objects.get(id=candidature_id)
            candidature.statut = statut
            candidature.save()
            return redirect('candidatures_recues')  # Redirection vers la liste des candidatures
        except Candidature.DoesNotExist:
            return redirect('candidatures_recues')

class CandidatureDetailView(DetailView):
    model = Candidature
    template_name = 'recruteur/candidatures_detail.html'
    context_object_name = 'candidature'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etudiant = self.object.etudiant  # Étudiant lié à la candidature
        context['etudiant'] = etudiant

        # Cherche le CV lié à l'utilisateur (directement via etudiant.user)
        try:
            cv = CV.objects.filter(user=etudiant).latest('date_upload')  # Utilise `etudiant.user`
            context['cv'] = cv
        except CV.DoesNotExist:
            context['cv'] = None  # Pas de CV trouvé

        return context

class ChangerStatutCandidatureView(UpdateView):
    model = Candidature
    fields = ['statut']  # Champ à modifier
    template_name = 'recruteur/changer_statut_candidature.html'

    def form_valid(self, form):
        form.save()  # Enregistrer le nouveau statut
        return redirect('candidatures_recues')  # Redirigez vers la liste des candidatures

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidature'] = self.object
        return context


# class ProfilEtudiantUpdateView(UpdateView):
#     model = Etudiant
#     form_class = EtudiantForm
#     template_name = 'etudiant/profil_etudiant_edit.html'
#     context_object_name = 'etudiant_form'
#     success_url = '/profil/'  # Redirection vers la page de consultation après modification
#
#     def get_object(self):
#         # Récupère l'objet Etudiant associé à l'utilisateur connecté
#         return self.request.user.etudiant
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Inclut aussi le formulaire de l'utilisateur dans le contexte
#         context['user_form'] = UserForm(instance=self.request.user)
#         return context
#
#     def form_valid(self, form):
#         # Sauvegarde les informations de l'étudiant
#         form.save()
#
#         # Sauvegarde les informations de l'utilisateur
#         user_form = UserForm(self.request.POST, instance=self.request.user)
#         if user_form.is_valid():
#             user_form.save()
#
#         return super().form_valid(form)


# Vue pour les candidatures
# class CandidatureListView(LoginRequiredMixin, ListView):
#     model = Candidature
#     template_name = 'etudiant/candidatures.html'
#     context_object_name = 'candidatures'
#
#     def get_queryset(self):
#         etudiant = Etudiant.objects.get(user=self.request.user)
#         return Candidature.objects.filter(etudiant=etudiant).order_by('-date_soumission')

# class CandidatureDeleteView(LoginRequiredMixin, TemplateView):
#     def post(self, request, pk, *args, **kwargs):
#         candidature = Candidature.objects.get(pk=pk)
#         if candidature.etudiant.user == request.user:
#             candidature.delete()
#             messages.success(request, "Candidature retirée avec succès.")
#         return redirect('candidatures')

# Vue pour la gestion des documents (CV, lettres de motivation)
# class DocumentManagementView(LoginRequiredMixin, TemplateView):
#     template_name = "etudiant/documents.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         etudiant = Etudiant.objects.get(user=self.request.user)
#         context['cv'] = etudiant.cv
#         return context

class ListeCandidaturesView(LoginRequiredMixin, ListView):
    model = Candidature
    template_name = 'service/liste_candidatures.html'
    context_object_name = 'candidatures'

    def get_queryset(self):
        return Candidature.objects.select_related('offre', 'etudiant').order_by('-date_soumission')

# class ListeOffresView(LoginRequiredMixin, ListView):
#     model = OffreStage
#     template_name = 'service/liste_offres.html'
#     context_object_name = 'offres'
#
#     def get_queryset(self):
#         return OffreStage.objects.all().order_by('-date_creation')
#
# class ModifierStatutOffreView(LoginRequiredMixin, UpdateView):
#     model = OffreStage
#     fields = ['statut']
#     template_name = 'service/modifier_statut_offre.html'
#
#     def get_success_url(self):
#         return reverse_lazy('liste_offres')


# Vue pour les entretiens
class EntretiensView(LoginRequiredMixin, TemplateView):
    template_name = "etudiant/entretiens.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etudiant = Etudiant.objects.get(user=self.request.user)
        context['entretiens'] = []  # À connecter à un modèle ou une logique future
        return context

# 6. Notifications
class NotificationView(LoginRequiredMixin, TemplateView):
    template_name = "etudiant/notifications.html"



# Vue pour les paramètres
class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "etudiant/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class HistoriqueCandidaturesView(LoginRequiredMixin, TemplateView):
    template_name = 'etudiant/historique.html'

    # Vous pouvez passer d'autres données spécifiques à l'étudiant ici si nécessaire
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidatures'] = self.request.user.etudiant.candidatures.all()  # Passer l'utilisateur connecté
        return context



# Vue de l'étudiant pour consulter ses candidatures
class MesCandidaturesView(LoginRequiredMixin, ListView):
    model = Candidature
    template_name = 'etudiant/mes_candidatures.html'
    context_object_name = 'candidatures'

    def get_queryset(self):
        # Filtrer les candidatures de l'étudiant connecté
        return Candidature.objects.filter(etudiant=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le compteur de candidatures
        context['candidatures_count'] = self.get_queryset().count()
        # Ajouter d'autres stats si nécessaire
        # context['vues_cv'] = 0  # À mettre à jour selon la logique métier pour les vues de CV
        return context


class ContratsListView(LoginRequiredMixin, ListView):
    model = Contrat
    template_name = 'recruteur/contrats.html'
    context_object_name = 'contrats'

    def get_queryset(self):
        # Affiche uniquement les contrats liés à l'entreprise
        return Contrat.objects.filter(entreprise=self.request.user.entreprise)

class CreerEntrepriseView(LoginRequiredMixin, CreateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'recruteur/creer_entreprise.html'

    def form_valid(self, form):
        # Associez l'entreprise au recruteur connecté
        entreprise = form.save(commit=False)
        entreprise.user = self.request.user
        entreprise.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('espace_recruteur')



class CreerOffreView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OffreStage
    form_class = OffreStageForm
    template_name = 'recruteur/offre_form.html'
    success_url = '/espace-recruteur/'  # Redirection après création

    def form_valid(self, form):
        # Vérifiez que l'utilisateur a bien une entreprise associée
        if not hasattr(self.request.user, 'entreprise'):
            return redirect('creer_entreprise')  # Sécurité supplémentaire, ne devrait pas se produire grâce à test_func
        form.instance.entreprise = self.request.user.entreprise
        messages.success(self.request, "L'offre de stage a été créée avec succès.")
        return super().form_valid(form)

    def test_func(self):
        # Vérifie si l'utilisateur est un recruteur ayant une entreprise associée
        if hasattr(self.request.user, 'entreprise'):
            return True
        # Redirige vers la création d'entreprise si aucune n'est associée
        return False

    def handle_no_permission(self):
        # Redirige les recruteurs sans entreprise vers la vue de création d'entreprise
        if hasattr(self.request.user.profile, 'user_type') and self.request.user.profile.user_type == 'recruiter':
            messages.warning(self.request, "Vous devez créer une entreprise avant de publier une offre.")
            return redirect('creer_entreprise')
        # Redirige vers une page d'erreur ou d'accueil si non autorisé
        messages.error(self.request, "Vous n'avez pas la permission d'accéder à cette page.")
        return redirect('accueil')

class GestionCandidaturesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'entreprise/gestion_candidatures.html'

    # Vous pouvez passer d'autres données spécifiques au recruteur ici si nécessaire
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offres = OffreStage.objects.filter(entreprise=self.request.user.entreprise)
        context['offres'] = offres
        return context

    def test_func(self):
        # Vérifie si l'utilisateur est un recruteur
        return hasattr(self.request.user, 'entreprise')

    def handle_no_permission(self):
        # Redirige vers une page d'erreur ou d'accueil si non autorisé
        return redirect('accueil')

# Vue pour l'espace service stage
class EspaceServiceStageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'service/base_service.html'

    def test_func(self):
        # Vérifie si l'utilisateur est un agent service stage
        return hasattr(self.request.user, 'servicestage')

    def handle_no_permission(self):
        # Redirection si l'utilisateur n'est pas autorisé
        return redirect('accueil')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données nécessaires pour les statistiques globales
        context['kpi_data'] = self.get_kpi_data()
        return context

    def get_kpi_data(self):
        # Méthode pour récupérer les données statistiques (mock pour l'instant)
        # Intégration avec Power BI viendra plus tard
        return {
            'nombre_offres': 150,
            'nombre_candidatures': 320,
            'nombre_contrats': 75,
            'taux_acceptation': '47%',
        }

class GestionCandidaturesServiceView(LoginRequiredMixin, TemplateView):
    template_name = 'service/gestion_candidatures.html'

    # Vous pouvez passer d'autres données spécifiques au service stage ici si nécessaire
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidatures'] = Candidature.objects.all()
        return context

class GestionEntreprisesView(LoginRequiredMixin, TemplateView):
    template_name = 'service/gestion_entreprises.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entreprises'] = Entreprise.objects.all()
        return context

class OffreStageSearchView(View):

    def post_search(request):
        query = None
        results = []
        search_form = SearchForm()

        # Si la requête GET contient un paramètre 'q'
        if 'q' in request.GET:
            search_form = SearchForm(request.GET)

            if search_form.is_valid():
                query = search_form.cleaned_data['query']

                # Recherche avec SearchVector (utilise les index de texte complet PostgreSQL)
                vector_search = SearchVector('titre', weight='A') + SearchVector('description', weight='B')
                query_search = SearchQuery(query)

                # Recherche de texte avec SearchRank
                # Vous pouvez décommenter cette ligne si vous souhaitez trier par pertinence.
                results = OffreStage.objects.annotate(
                    search=vector_search,
                    rank=SearchRank(vector_search, query_search)
                ).filter(search=query_search).order_by('-rank')

                # Recherche avec TrigramSimilarity (basé sur la similarité de texte)
                results = OffreStage.objects.annotate(
                    similarity=TrigramSimilarity('titre', query) + TrigramSimilarity('description', query)
                ).filter(similarity__gt=0.1).order_by('-similarity')

        return render(request, 'offres/offres_list.html', {
            'search_form': search_form,
            'query': query,
            'results': results
        })

class OffreStageListView(ListView):
    model = OffreStage
    template_name = 'offres/offres_list.html'
    context_object_name = 'offres'
    paginate_by = 6

    def get_queryset(self):
        # Récupérer la requête de recherche depuis l'URL
        search_query = self.request.GET.get('search', '')
        # Filtrer les offres si un terme de recherche est fournit
        queryset = OffreStage.objects.all().order_by('-date_publication')



        if search_query:
            queryset = queryset.filter(
                Q(titre__icontains=search_query) | # Recherche dans le titre
                Q(entreprise__nom__icontains=search_query) | # Recherche dans l'entreprise
                Q(localisation__icontains=search_query) | # Recherche dans la localisation
                Q(description__icontains=search_query) # Recherche dans la description
            )

        return queryset

    def get_context_data(self, **kwargs):
        # Ajouter le total des offres à context
        context = super().get_context_data(**kwargs)
        context['total_offres'] = OffreStage.objects.count()  # Compter toutes les offres dans la base
        return context

class OffreStageDetailView(DetailView):
    model = OffreStage
    template_name = 'offres/offres_detail.html'
    context_object_name = 'offre'

class PostulerView(LoginRequiredMixin, CreateView):
    model = Candidature
    fields = ['cv']
    template_name = 'etudiant/postuler.html'

    def form_valid(self, form):
        # Associer l'étudiant connecté et l'offre
        form.instance.etudiant = self.request.user
        offre = get_object_or_404(OffreStage, pk=self.kwargs['pk'])
        form.instance.offre = offre

        # Vérification : Si une candidature existe déjà, empêcher la soumission
        if Candidature.objects.filter(etudiant=self.request.user, offre=offre).exists():
            messages.error(self.request, "Vous avez déjà postulé à cette offre.")
            return redirect('espace_etudiant')

        # Récupérer l'ID du CV sélectionné
        cv_id = self.request.POST.get('cv')
        if not cv_id:
            messages.error(self.request, "Veuillez sélectionner un CV avant de postuler.")
            return self.form_invalid(form)

        # Vérifier l'existence et la validité du CV
        cv = get_object_or_404(CV, pk=cv_id, user=self.request.user)
        if not cv.fichier:
            messages.error(self.request, "Le CV sélectionné ne contient aucun fichier.")
            return self.form_invalid(form)

        # Associer le CV à la candidature
        form.instance.cv = cv
        messages.success(self.request, "Votre candidature a été enregistrée avec succès.")
        return super().form_valid(form)


    def get_success_url(self):
        return reverse_lazy('espace_etudiant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offre = get_object_or_404(OffreStage, pk=self.kwargs['pk'])
        context['offre'] = offre
        context['cv_list'] = CV.objects.filter(user=self.request.user)
        context['can_postuler'] = context['cv_list'].exists()  # Vérifie s'il existe des CV
        return context



# @login_required
# def postuler_offre(request, offre_id):
#     offre = get_object_or_404(OffreStage, pk=offre_id)
#
#     # Vérifiez si l'utilisateur connecté est un étudiant
#     if not hasattr(request.user, 'etudiant'):
#         messages.error(request, "Seuls les étudiants peuvent postuler aux offres de stage.")
#         return redirect('offre_detail', pk=offre_id)  # Restez sur la page de détail de l'offre
#
#     # Vérifier que l'étudiant ait déjà postulé à cette offre
#     if Candidature.objects.filter(etudiant=request.user.etudiant, stage=offre).exists():
#         messages.info(request, "Vous avez déjà postulé à cette offre.")
#     else:
#         # Créer et enregistrer la candidature
#         Candidature.objects.create(stage=offre, etudiant=request.user.etudiant)
#         messages.success(request, "Votre candidature a été envoyée avec succès !")
#
#     return redirect('offre_detail', pk=offre_id)

@login_required
def suivre_candidatures(request):
    candidatures = Candidature.objects.filter(etudiant=request.user.etudiant)
    return render(request, 'candidatures/suivre_candidatures.html', {"candidatures": candidatures})

@login_required
def gerer_contrats(request):
    contrats = Contrat.objects.filter(entreprise=request.user.entreprise)
    return render(request, 'contrats/gerer_contrats.html', {"contrats": contrats})

