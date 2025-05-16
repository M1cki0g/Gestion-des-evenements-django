import csv
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from crud_event.models import evenement,participation,Organisateur
from django import forms
from django.contrib import messages
from crud_event.models import Organisateur

@staff_member_required
def mon_dashboard(request):
    from django.db.models import Count, Avg, Sum
    from django.utils import timezone
    from datetime import timedelta
    
    # Date actuelle et début du mois
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0)
    
    # Statistiques de base
    nb_users = User.objects.count()
    nb_events = evenement.objects.count()
    nb_participations = participation.objects.count()
    org = Organisateur.objects.count()
    
    # Nouvelles statistiques
    upcoming_events = evenement.objects.filter(date__gt=now).count()
    monthly_revenue = participation.objects.filter(
        date_inscription__gte=start_of_month
    ).count() * 100  # Exemple: 100€ par participation
    
    # Calcul du taux de remplissage
    total_places = evenement.objects.aggregate(Sum('nombre_places'))['nombre_places__sum'] or 0
    avg_fill_rate = (nb_participations / total_places * 100) if total_places > 0 else 0
    
    # Top catégories
    top_categories = evenement.objects.values('categorie').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Moyenne des participants par événement
    avg_participants = evenement.objects.aggregate(
        Avg('nombre_participants')
    )['nombre_participants__avg'] or 0
      # Données pour le graphique des catégories
    categories_data = list(top_categories)
    categories_labels = [cat['categorie'] for cat in categories_data]
    categories_counts = [cat['count'] for cat in categories_data]

    # Données pour l'évolution des inscriptions sur 6 mois
    last_6_months = []
    months_data = []
    for i in range(5, -1, -1):
        date = start_of_month - timedelta(days=30 * i)
        month_name = date.strftime('%B')
        count = participation.objects.filter(
            date_inscription__year=date.year,
            date_inscription__month=date.month
        ).count()
        last_6_months.append(month_name)
        months_data.append(count)

    # Données pour le taux de participation par événement (top 5)
    events_participation = evenement.objects.annotate(
        participation_rate=Count('participation') * 100.0 / Sum('nombre_places')
    ).order_by('-participation_rate')[:5]
    events_labels = [event.nom_event for event in events_participation]
    events_rates = [round(event.participation_rate or 0, 1) for event in events_participation]
    
    # Dernières activités
    derniers_utilisateurs = User.objects.order_by('-date_joined')[:3]
    derniers_evenements = evenement.objects.filter(date__gte=now - timedelta(days=7)).order_by('-date')[:3]
    dernieres_participations = participation.objects.select_related('participan', 'event').order_by('-date_inscription')[:3]

    context = {
        'nb_users': nb_users,
        'nb_events': nb_events,
        'nb_participations': nb_participations,
        'nb_org': org,
        'upcoming_events': upcoming_events,
        'monthly_revenue': monthly_revenue,
        'avg_fill_rate': round(avg_fill_rate, 1),
        'avg_participants': round(avg_participants, 1),
        'top_categories': top_categories,
        # Données pour les graphiques
        'categories_labels': categories_labels,
        'categories_counts': categories_counts,
        'months_labels': last_6_months,
        'months_data': months_data,
        'events_labels': events_labels,
        'events_rates': events_rates,
        # Dernières activités
        'derniers_utilisateurs': derniers_utilisateurs,
        'derniers_evenements': derniers_evenements,
        'dernieres_participations': dernieres_participations,
    }
    
    return render(request, 'dashboard.html', context)

# @staff_member_required
# def admin_events(request):
#     evenements = evenement.objects.all()
#     return render(request, 'admin_events.html', {'evenements': evenements})

@staff_member_required
def admin_users(request):
    utilisateurs = User.objects.all()
    return render(request, 'admin_users.html', {'utilisateurs': utilisateurs})

@staff_member_required
def admin_organisateur(request):
    
    organisateur = Organisateur.objects.all()
    return render(request, 'list_organisateur.html', {'Organisateurs': organisateur})
# CRUD for events 
class EventListView(ListView):
    model = evenement
    template_name = 'admin_events.html'
    context_object_name = 'events'

class EventCreateView(CreateView):
    model = evenement
    fields = ['nom_event', 'image', 'date', 'lieu', 'categorie', 'description']
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')
    def form_valid(self, form):
        # Check if the user is admin/staff
        if self.request.user.is_staff:
            form.instance.is_validated = True
        else:   
            form.instance.is_validated = False
        
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)
    
class EventUpdateView(UpdateView):
    model = evenement
    fields = ['nom_event', 'image', 'date', 'lieu', 'categorie', 'description']
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')
    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.fields['date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    #     return form

class EventDeleteView(DeleteView):
    model = evenement
    success_url = reverse_lazy('event_list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
    # success_url = reverse_lazy('event_list')



# CRUD for Users
# class UserListView(ListView):
#     model = User
#     template_name = 'user_list.html'
#     context_object_name = 'users'

class UserUpdateView(UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'user_form.html'
    success_url = reverse_lazy('admin_users')  # ou 'user_list' selon ce que tu veux

class UserDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('admin_users')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

class AjouterUtilisateurView(CreateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'password']
    template_name = 'ajouter_utilisateur.html'
    success_url = reverse_lazy('admin_users')  # Redirige vers la liste des utilisateurs après la création

    def form_valid(self, form):
        # Hash the password before saving the user
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)




class ParticipationListView(ListView):
    model = participation
    template_name = "list_particpation.html"
    context_object_name = "participations"
    ordering = ['-date_inscription']  


class ParticipationCreateView(CreateView):
    model = participation
    template_name = "add_participation.html"
    fields = ['participan', 'event', 'phone_num']
    success_url = reverse_lazy('participations')

    def form_valid(self, form):
        event = form.cleaned_data['event']

        if event.nombre_places <= 0:
            messages.error(self.request, "Cet événement est complet.")
            return redirect('participation_add')
        
        # Vérifier si l'utilisateur est déjà inscrit à cet événement
        existing_participation = participation.objects.filter(
            participan=form.cleaned_data['participan'],
            event=form.cleaned_data['event']
        ).exists()

        if existing_participation:
            messages.error(self.request, "Cet utilisateur est déjà inscrit à cet événement.")
            return redirect('participation_add')  # Redirige vers le formulaire d'ajout

        # Réduire le nombre de places disponibles
        event.nombre_places -= 1
        event.nombre_participants += 1
        event.save()

        # Remplir automatiquement name_event
        form.instance.name_event = form.instance.event.nom_event
        # Remplir automatiquement participant avec le nom complet ou le username
        form.instance.participant = (
            form.instance.participan.get_full_name() or form.instance.participan.username
        )
            

        return super().form_valid(form)















class ParticipationUpdateView(UpdateView):
    model = participation
    template_name = "edit_participation.html"
    fields = ['participan', 'event', 'phone_num']  # Choix de l'utilisateur, l'événement, et téléphone
    success_url = reverse_lazy('participations')



class ParticipationDeleteView(DeleteView):
    model = participation
    template_name = "delete_participation.html"  # On va créer une page de confirmation
    success_url = reverse_lazy('participations')



def evenements_en_attente(request):
    # Récupérer tous les événements en attente de validation (supposons que tu as un champ 'valide' qui définit si l'événement est validé ou non)
    evenements = evenement.objects.filter(is_validated=False) # Exemple, adapte en fonction de ton modèle
    return render(request, 'validerEvenements.html', {'evenements': evenements})


def valider_evenement(request, id):
    if request.method == 'POST':
        evt = get_object_or_404(evenement, id=id)
        evt.is_validated = True
        evt.save()
        if not Organisateur.objects.filter(user=evt.organisateur).exists():
            Organisateur.objects.create(
                user=evt.organisateur,
                nom=evt.organisateur.last_name,
                prenom=evt.organisateur.first_name,
                email=evt.organisateur.email,
            )

        messages.success(request, f"L'événement '{evt.nom_event}' a été validé avec succès.")
    return redirect('evenements_en_attente')

def refuser_evenement(request, id):
    if request.method == 'POST':
        evt = get_object_or_404(evenement, id=id)
        evt.delete()  # Supprimer l'événement
    return redirect('evenements_en_attente')



@staff_member_required
def download_participants_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="participants.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Participant Name', 'Event Name', 'Phone Number', 'Date of Registration'])

    # Fetch all participations
    participations = participation.objects.select_related('participan', 'event').all()

    # Write data rows
    for p in participations:
        writer.writerow([
            p.participan.get_full_name() or p.participan.username,
            p.event.nom_event,
            p.phone_num,
            p.date_inscription
        ])

    return response


# Ajouter un organisateur
class OrganisateurCreateView(CreateView):
    model = Organisateur
    fields = ['user', 'nom', 'prenom', 'email']
    template_name = 'organisateur_form.html'
    success_url = reverse_lazy('admin_org')

# Modifier un organisateur
class OrganisateurUpdateView(UpdateView):
    model = Organisateur
    fields = ['user', 'nom', 'prenom', 'email']
    template_name = 'organisateur_form.html'
    success_url = reverse_lazy('admin_org')

# Supprimer un organisateur
class OrganisateurDeleteView(DeleteView):
    model = Organisateur
    success_url = reverse_lazy('admin_org')

    def get(self, request, *args, **kwargs):
        # Supprime directement sans confirmation
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Supprime l'objet et redirige sans afficher de template
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Organisateur supprimé avec succès.")
        return redirect(self.success_url)