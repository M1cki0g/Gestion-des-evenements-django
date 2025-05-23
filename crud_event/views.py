from datetime import datetime
import math
from pyexpat.errors import messages
from django.shortcuts import render,HttpResponse
from .models import evenement, paiement
from crud_event.models import evenement, participation
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .models import CustomUserCreationForm,evenement,EvenementForm  # Importez le formulaire personnalisé
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404
from .models import participation
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
import os
from io import BytesIO
import qrcode
from .models import Organisateur
from PIL import Image as PILImage

# Create your views here.




@login_required
def creer_evenement(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.organisateur = request.user
                event.organisateur_name = request.user.username
                
                # Gestion de l'image
                if 'image' in request.FILES:
                    # Assurez-vous que le répertoire existe
                    from django.conf import settings
                    import os
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                
                # Auto-valider si l'utilisateur est admin/staff
                event.is_validated = True if request.user.is_staff else False
                event.save()
                
                # Message de succès
                if request.user.is_staff:
                    messages.success(request, "Votre événement a été créé avec succès.")
                else:
                    messages.success(request, "Votre événement a été créé avec succès, en attente de validation par l'administrateur.")
                
                return redirect('creerEvent')
            except Exception as e:
                print(f"Erreur lors de la création de l'événement: {e}")
                messages.error(request, f"Une erreur s'est produite: {e}")
        else:
            print(f"Formulaire non valide: {form.errors}")
            messages.error(request, f"Données invalides: {form.errors}")
    else:
        form = EvenementForm()

    return render(request, 'creerEvent.html', {'form': form})



def home(request):
    evenements = evenement.objects.filter(is_validated=True)
    return render(request, 'home.html', {'evenements': evenements})


#def liste_evenements(request):
   # evenements = evenement.objects.all()
   # return render(request, 'home.html', {'evenements': evenements})


@login_required
def register_event(request, event_id):
    event = get_object_or_404(evenement, id=event_id)
    if request.user.is_staff:
        return redirect('home')
    # Vérifier s'il reste des places disponibles
    if event.nombre_places <= 0:
        messages.error(request, "Désolé, il n'y a plus de places disponibles pour cet événement.")
        return render(request, 'register.html', {
            'event': event,
            'no_places_available': True
        })
    # Vérifier si l'organisateur de s'inscrire a son propre event
    if event.organisateur == request.user:
        return redirect('home')

    # Vérifier si l'utilisateur est déjà inscrit
    if participation.objects.filter(participan=request.user, event=event).exists():
        messages.warning(request, f"Vous êtes déjà inscrit à l'événement '{event.nom_event}'.")
        return render(request, 'register.html', {
            'event': event,
            'already_registered': True
        })

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')  
        phone_num = request.POST.get('phone_num')  
        payment_method = request.POST.get('payment_method')

        # Payment details
        card_number = request.POST.get('card_number')
        card_holder_name = request.POST.get('card_holder_name')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Validate payment date format
        try:
            if '/' in expiry_date:
                month, year = map(int, expiry_date.split('/'))
                if len(str(year)) == 2:
                    year = 2000 + year
                expiry_date_obj = datetime(year, month, 1)
            else:
                messages.error(request, "Format de date d'expiration invalide. Utilisez le format MM/YY.")
                return render(request, 'register.html', {'event': event})
        except (ValueError, AttributeError):
            messages.error(request, "Date d'expiration invalide.")
            return render(request, 'register.html', {'event': event})

        # Validate required fields
        if not all([name, email, phone_num, card_number, card_holder_name, expiry_date, cvv, payment_method]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'register.html', {'event': event})

        try:
            # Vérifier à nouveau le nombre de places avant de créer la participation
            if event.nombre_places <= 0:
                messages.error(request, "Désolé, il n'y a plus de places disponibles pour cet événement.")
                return render(request, 'register.html', {'event': event})

            # Save participation
            participation_instance = participation.objects.create(
                participan=request.user,
                event=event,
                name_event=event.nom_event,
                phone_num=phone_num,
                participant=name,
                email=email
            )

            # Save payment with amount
            paiement_instance = paiement.objects.create(
                user_id=request.user,
                event=event,
                participation=participation_instance,
                card_number=card_number,
                card_holder_name=card_holder_name,
                expiry_date=expiry_date_obj,
                cvv=cvv,
                payment_method=payment_method,
                amount=event.price
            )



            # Décrémenter le nombre de places et incrémenter le nombre de participants
            event.nombre_places -= 1
            event.nombre_participants += 1
            event.save()

            messages.success(request, f"Paiement de {event.price}$ et inscription réussis.")
            return render(request, 'register.html', {
                'event': event,
                'show_success_modal': True,
                'participation_id': participation_instance.id
            })

        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de l'enregistrement: {str(e)}")
            return render(request, 'register.html', {'event': event})

    return render(request, 'register.html', {'event': event})




@login_required
def generate_ticket(request, participation_id):
    participation_obj = get_object_or_404(participation, id=participation_id, participan=request.user)
    event = participation_obj.event

    # Créer un buffer en mémoire
    buffer = BytesIO()
    
    # Créer le PDF en mode paysage
    width, height = landscape(A4)
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Palette de couleurs
    main_blue = (0.114, 0.345, 0.949)  # #1D58F2 - Bleu vif
    white = (1, 1, 1)
    black = (0, 0, 0)
    
    # Fond blanc
    p.setFillColorRGB(*white)
    p.rect(0, 0, width, height, fill=True)
    
    # Section principale (2/3 gauche)
    main_width = (width * 2/3) - 20  # Largeur de la section principale
    
    # Titre "SPECIAL NIGHT"
    p.setFillColorRGB(*main_blue)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(40, height-80, "SPECIAL NIGHT")
    
    # Sous-titre avec le nom de l'événement en grand
    p.setFont("Helvetica-Bold", 32)
    p.drawString(40, height-130, event.nom_event.upper())
    
    # Informations détaillées
    y_start = height - 200
    x_col1 = 40
    x_col2 = main_width/2
    
    # Première colonne
    p.setFillColorRGB(*main_blue)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(x_col1, y_start, "1st")
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(*black)
    p.drawString(x_col1, y_start-30, participation_obj.participant)
    
    # Deuxième colonne
    p.setFillColorRGB(*main_blue)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(x_col2, y_start, "2nd")
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(*black)
    p.drawString(x_col2, y_start-30, participation_obj.email)
    
    # Date et heure
    y_datetime = y_start - 80
    p.setFillColorRGB(*main_blue)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(x_col1, y_datetime, "DATE")
    p.drawString(x_col2, y_datetime, "TIME")
    
    p.setFillColorRGB(*black)
    p.setFont("Helvetica", 14)
    p.drawString(x_col1, y_datetime-30, event.date.strftime('%B %d - %Y'))
    p.drawString(x_col2, y_datetime-30, event.date.strftime('%H:%M'))
    
    # Boutons Sponsor
    y_sponsor = y_datetime - 100
    sponsor_width = 100
    sponsor_height = 30
    for i in range(3):
        x_sponsor = x_col1 + (i * (sponsor_width + 20))
        # Rectangle bleu
        p.setFillColorRGB(*main_blue)
        p.roundRect(x_sponsor, y_sponsor, sponsor_width, sponsor_height, 6, fill=True)
        # Texte blanc
        p.setFillColorRGB(*white)
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(x_sponsor + sponsor_width/2, y_sponsor + 10, "SPONSOR")
    
    # Adresse en bas
    p.setFillColorRGB(*black)
    p.setFont("Helvetica", 12)
    p.drawString(x_col1, y_sponsor-40, event.lieu)
    
    # Section du ticket (1/3 droite)
    ticket_x = width * 2/3
    ticket_width = width/3
    
    # Rectangle bleu pour le ticket
    p.setFillColorRGB(*main_blue)
    p.rect(ticket_x, 0, ticket_width, height, fill=True)
    
    # Titre du ticket
    p.setFillColorRGB(*white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(ticket_x + 20, height-80, "EVENT TICKET 2025")
    
    # QR Code
    qr = qrcode.QRCode(version=1, box_size=3, border=0)
    qr_data = f"Event: {event.nom_event}\nParticipant: {participation_obj.participant}\nTicket: #{participation_obj.id:06d}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Position du QR code centré
    qr_size = 120
    qr_x = ticket_x + (ticket_width - qr_size)/2
    qr_y = height/2
    p.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
    
    # VIP en grand
    p.setFillColorRGB(*white)
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(ticket_x + ticket_width/2, qr_y-80, "VIP")
    
    # Code-barres en bas (simulé avec un rectangle blanc)
    barcode_y = 80
    barcode_width = ticket_width * 0.8
    barcode_x = ticket_x + (ticket_width - barcode_width)/2
    p.setFillColorRGB(*white)
    p.rect(barcode_x, barcode_y, barcode_width, 30, fill=True)
    
    # Finaliser le PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    
    # Nom de fichier professionnel
    event_name_clean = ''.join(e for e in event.nom_event if e.isalnum() or e == ' ').strip().replace(' ', '_')
    filename = f"Event_Ticket_{event_name_clean}_{participation_obj.id}.pdf"
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def participation_history(request):
    participations = participation.objects.filter(participan=request.user).order_by('-date_inscription')
    return render(request, 'historique.html', {'participations': participations})





@login_required
def annuler_participation(request, participation_id):
    participation_instance = get_object_or_404(participation, id=participation_id, participan=request.user)
    # Réincrémenter le nombre de places
    event = participation_instance.event
    event.nombre_places += 1
    event.nombre_participants -= 1
    event.save()
    # Supprimer la participation
    participation_instance.delete()
    messages.success(request, "Votre participation a été annulée avec succès.")
    return redirect('history')


@login_required
def my_events(request):
    # Récupérer les événements créés par l'utilisateur connecté
    events = evenement.objects.filter(organisateur=request.user).order_by('-date')
    return render(request, 'Myevents.html', {'events': events})

@login_required
def liste_participants(request,event_id):
      Event = get_object_or_404(evenement, id=event_id, organisateur=request.user)
      participants = participation.objects.filter(event=Event)
      return render (request,'list_of_participation.html',{'participants':participants}) 





@login_required
def annuler_evenement(request, event_id):
    # Récupérer l'événement
    event = get_object_or_404(evenement, id=event_id, organisateur=request.user)
    
    if request.method == 'POST':
        # Supprimer toutes les participations associées
        participations = participation.objects.filter(event=event)
        for p in participations:
            p.delete()
        
        # Supprimer l'événement
        event.delete()
        messages.success(request, "L'événement a été annulé avec succès.")
        return redirect('my_events')
    
    return redirect('my_events')


