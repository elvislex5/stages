
from django.urls import path

from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register_view'),
    path('offres/', views.consulter_offres, name='consulter_offres'),
    path('postuler/<int:offre_id>/', views.postuler_offre, name='postuler_offre'),
    path('candidatures/', views.suivre_candidatures, name='suivre_candidatures'),
    path('entreprise/contrats/', views.gerer_contrats, name='gerer_contrats'),

]
