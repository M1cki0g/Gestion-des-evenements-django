# urls.py

from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required
from .views import (
   EventListView, EventCreateView, EventUpdateView, EventDeleteView,
    ParticipationListView, ParticipationDeleteView, UserDeleteView,
     UserUpdateView, 
    ParticipationCreateView, ParticipationUpdateView,AjouterUtilisateurView ,ParticipationCreateView,
    # UserListView
    EventListView, EventCreateView, EventUpdateView, EventDeleteView, ParticipationCreateView, ParticipationDeleteView, ParticipationListView, ParticipationUpdateView,
    UserUpdateView,AjouterUtilisateurView 
    # UserListView,
)


urlpatterns = [
     
    path('dashboard/', views.mon_dashboard, name='mon_dashboard'),
    # path('admin_events/', views.admin_events, name='admin_events'),
    path('admin_users/', views.admin_users, name='admin_users'),
     path('admin_organisateur/', views.admin_organisateur, name='admin_org'),
    # path('admin_participations/', views.admin_participations, name='admin_participations'),
# Event URLs
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/create/', login_required(EventCreateView.as_view()), name='event_create'),
    path('events/update/<int:pk>/', EventUpdateView.as_view(), name='event_update'),
    path('events/delete/<int:pk>/', EventDeleteView.as_view(), name='event_delete'),

# Participation URLs
    path('participations/', ParticipationListView.as_view(), name='participations'),
    path('participations/add/', ParticipationCreateView.as_view(), name='participation_add'),
    path('participations/<int:pk>/edit/', ParticipationUpdateView.as_view(), name='participation_edit'),
    path('participations/<int:pk>/delete/', ParticipationDeleteView.as_view(), name='participation_delete'),


# User URLs
    # path('users/', UserListView.as_view(), name='user_list'),
  
    path('users/update/<int:pk>/', UserUpdateView.as_view(), name='modifier_utilisateur'),
    path('users/ajouter/', AjouterUtilisateurView.as_view(), name='ajouter_utilisateur'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='supprimer_utilisateur'),  # URL pour supprimer un utilisateur
   

# Events validation

    path('evenements-en-attente/', views.evenements_en_attente, name='evenements_en_attente'),
    path('valider-evenement/<int:id>/', views.valider_evenement, name='valider_evenement'),  # URL pour la validation
    path('refuser-evenement/<int:id>/', views.refuser_evenement, name='refuser_evenement'),  # URL pour le refus
    path('download-participants/', views.download_participants_csv, name='download_participants_csv'),
 
# Organisateur URLs
 path('organisateurs/add/', views.OrganisateurCreateView.as_view(), name='organisateur_add'),
    path('organisateurs/<int:pk>/edit/', views.OrganisateurUpdateView.as_view(), name='organisateur_edit'),
    path('organisateurs/<int:pk>/delete/', views.OrganisateurDeleteView.as_view(), name='organisateur_delete'),
]

