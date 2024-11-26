from tkinter.font import names

from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='accueil'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register_view'),
    # path('profil/', views.StudentProfileView.as_view(), name='profil_etudiant'),
    path('espace-etudiant/', views.EspaceEtudiantView.as_view(), name='espace_etudiant'),
    # path('candidatures/delete/<int:pk>/', views.CandidatureDeleteView.as_view(), name='delete_candidature'),
    path('profil/', views.ProfilEtudiantDetailView.as_view(), name='profil_etudiant'),
    path('formations/', views.FormationListView.as_view(), name='formations_list'),
    path('formations/ajouter/', views.FormationCreateView.as_view(), name='formation_create'),
    path('formations/<int:pk>/modifier/', views.FormationUpdateView.as_view(), name='formation_update'),
    path('formations/<int:pk>/supprimer/', views.FormationDeleteView.as_view(), name='formation_delete'),
    path('experiences/', views.ExperienceProfessionnelleListView.as_view(), name='experiences_list'),
    path('experiences/ajouter/', views.ExperienceProfessionnelleCreateView.as_view(), name='experience_create'),
    path('experiences/<int:pk>/modifier/', views.ExperienceProfessionnelleUpdateView.as_view(), name='experience_update'),
    path('experiences/<int:pk>/supprimer/', views.ExperienceProfessionnelleDeleteView.as_view(), name='experience_delete'),
    path('competences/', views.CompetenceListView.as_view(), name='competences_list'),
    path('competences/ajouter/', views.CompetenceCreateView.as_view(), name='competence_create'),
    path('competences/<int:pk>/modifier/', views.CompetenceUpdateView.as_view(), name='competence_update'),
    path('competences/<int:pk>/supprimer/', views.CompetenceDeleteView.as_view(), name='competence_delete'),
    path('documents/', views.DocumentOptionsView.as_view(), name='document_options'),
    path('documents/cv/', views.CVDetailView.as_view(), name='cv_detail'),
    path('documents/cv/upload/', views.CVUploadView.as_view(), name='cv_upload'),
    path('documents/cv/delete/', views.CVDeleteView.as_view(), name='cv_delete'),
    path('documents/lettre-motivation/', views.LettreMotivationDetailView.as_view(), name='lettre_motivation_detail'),
    path('documents/lettre-motivation/upload-lettre-motivation/', views.LettreMotivationUpdateView.as_view(), name='upload_lettre_motivation'),

    path('documents/cv/mon-cv/', views.CVGenerateView.as_view(), name='generate_cv'),
    path('documents/cv/mon-cv/pdf/', views.CVGeneratePDFView.as_view(), name='generate_cv_pdf'),

    # path('documents/', views.DocumentManagementView.as_view(), name='documents'),
    path('entretiens/', views.EntretiensView.as_view(), name='entretiens'),
    path('notifications/', views.NotificationView.as_view(), name='notifications'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('historique-candidatures/', views.HistoriqueCandidaturesView.as_view(), name='historique_candidatures'),
    path('espace-recruteur/', views.EspaceRecruteurView.as_view(), name='espace_recruteur'),
    path('recruteur/offre/<int:pk>/', views.OffreDetailRecruteurView.as_view(), name='detail_offre_recruteur'),
    path('mes-offres/', views.OffresRecruteurListView.as_view(), name='mes_offres'),
    path('entreprise/', views.EntrepriseRecruteurDetailView.as_view(), name='informations_entreprise'),
    path('candidatures/', views.CandidaturesReçuesListView.as_view(), name='candidatures_recues'),
    path('candidatures/<int:pk>/details', views.CandidatureDetailView.as_view(), name='candidatures_detail'),
    path('candidature/<int:pk>/changer-statut/', views.ChangerStatutCandidatureView.as_view(),
         name='changer_statut_candidature'),
    path('mes-candidatures/', views.MesCandidaturesView.as_view(), name='mes_candidatures'),

    path('contrats/', views.ContratsListView.as_view(), name='contrats'),

    path('creer-entreprise/', views.CreerEntrepriseView.as_view(), name='creer_entreprise'),

    path('creer-offre/', views.CreerOffreView.as_view(), name='creer_offre'),
    path('gestion-candidatures/', views.GestionCandidaturesView.as_view(), name='gestion_candidatures'),
    path('espace-service-stage/', views.EspaceServiceStageView.as_view(), name='espace_service_stage'),
    path('gestion-candidatures/', views.GestionCandidaturesServiceView.as_view(), name='gestion_candidatures_service'),
    path('gestion-entreprises/', views.GestionEntreprisesView.as_view(), name='gestion_entreprises'),
    path('offres/', views.OffreStageListView.as_view(), name='offre_list'),
    path('offres/<int:entreprise_id>/', views.OffreStageListView.as_view(), name='offre_list'),
    path('entreprises/', views.EntrepriseListView.as_view(), name='entreprise_list'),
    path('entreprise/<int:pk>/', views.EntrepriseDetailView.as_view(), name='entreprise_detail'),
    path('offres/search/', views.OffreStageSearchView.as_view(), name='search_offres'),
    path('offres/<int:pk>/postuler/', views.PostulerView.as_view(), name='postuler'),
    path('offre/<int:pk>/', views.OffreStageDetailView.as_view(), name='offre_detail'),
    # path('candidatures/', views.suivre_candidatures, name='suivre_candidatures'),
    path('entreprise/contrats/', views.gerer_contrats, name='gerer_contrats'),

]
