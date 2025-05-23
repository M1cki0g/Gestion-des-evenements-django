from django.db import models
from django import forms
from django.contrib.auth.forms import UserCreationForm
import os
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django import forms

# Create your models here.

def file_path(instance, filename):
    timenow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Safe filename creation
    filename = f"{timenow}_{filename}"
    # Ensure uploads directory exists
    upload_dir = os.path.join('media', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    # Return just the path relative to MEDIA_ROOT
    return os.path.join('uploads', filename)

# class personne(models.Model):
#     id = models.AutoField(primary_key=True)
#     nom = models.CharField(max_length=200)
#     prenom = models.CharField(max_length=200)
#     num_tel = models.IntegerField() 

# class organisateur(personne):
#     email = models.EmailField(max_length=200, unique=True)
#     description = models.TextField()


class evenement(models.Model):
    id = models.AutoField(primary_key=True)
    nom_event = models.CharField(max_length=200)
    image = models.ImageField(upload_to=file_path, blank=True, null=True)
    # Suppression temporaire de image_url pour résoudre l'erreur en production
    # image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional external image URL")
    date = models.DateTimeField()
    lieu = models.CharField(max_length=200)
    nombre_places = models.IntegerField(default=2)
    categorie = models.CharField(max_length=200)
    description = models.TextField(max_length=2000 , blank=True, null=True)
    organisateur = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def get_image_url(self):
        """Return a valid image URL, using default if none available"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Liste d'images par défaut pour chaque catégorie
        default_images = {
            'Musique': 'https://raw.githubusercontent.com/M1cki0g/Gestion-des-evenements-django/master/gestion_des_evenements/static/images/music_event.jpg',
            'Sport': 'https://raw.githubusercontent.com/M1cki0g/Gestion-des-evenements-django/master/gestion_des_evenements/static/images/sport_event.jpg',
            'Technologie': 'https://raw.githubusercontent.com/M1cki0g/Gestion-des-evenements-django/master/gestion_des_evenements/static/images/tech_event.jpg',
            'Art': 'https://raw.githubusercontent.com/M1cki0g/Gestion-des-evenements-django/master/gestion_des_evenements/static/images/art_event.jpg',
            'default': 'https://raw.githubusercontent.com/M1cki0g/Gestion-des-evenements-django/master/gestion_des_evenements/static/images/event_web.jpg'
        }
        
        # Log de débogage pour comprendre ce qui se passe
        logger.info(f"get_image_url called for event {self.id}: {self.nom_event}")
        if self.image:
            logger.info(f"Event has image attribute: {self.image}")
        else:
            logger.info("Event has no image attribute set")
            
        # Essayer d'utiliser l'image téléchargée
        if self.image:
            try:
                # Vérifier si l'attribut name existe
                if hasattr(self.image, 'name'):
                    logger.info(f"Image name: {self.image.name}")
                
                # Vérifier si l'attribut url existe
                if hasattr(self.image, 'url'):
                    image_url = self.image.url
                    logger.info(f"Image URL: {image_url}")
                    return image_url
                else:
                    logger.warning("Image object has no 'url' attribute")
            except Exception as e:
                logger.error(f"Exception when accessing image.url: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Vérifier la configuration S3
        try:
            from django.conf import settings
            if hasattr(settings, 'USE_S3') and settings.USE_S3:
                logger.info(f"S3 is enabled, bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
                logger.info(f"Media URL from settings: {settings.MEDIA_URL}")
            else:
                logger.info("S3 is not enabled in settings")
        except Exception as e:
            logger.error(f"Error checking S3 settings: {str(e)}")
        
        # Utiliser une image par défaut basée sur la catégorie
        default_url = default_images.get(self.categorie, default_images['default'])
        logger.info(f"Using default image: {default_url}")
        return default_url
    organisateur_name = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=2.00)
    is_validated = models.BooleanField(default=False)
    nombre_participants = models.IntegerField(default=0)
   
    def __str__(self):
        return self.nom_event
    def save(self, *args, **kwargs):
        if self.organisateur and not self.organisateur_name:
            self.organisateur_name = self.organisateur.username
        super(evenement, self).save(*args, **kwargs)


class participation(models.Model):
      participan=models.ForeignKey(User,on_delete=models.CASCADE)
      event=models.ForeignKey(evenement, on_delete=models.CASCADE)
      date_inscription = models.DateTimeField(default=timezone.now)
      phone_num=models.CharField(max_length=200, blank=True, null=True)
      name_event=models.CharField(max_length=200, blank=True, null=True)
      participant=models.CharField(max_length=200, blank=True, null=True)
      email=models.EmailField(max_length=200, blank=True, null=True)
      def __str__(self):
        return f"{self.participan.username} participe à l'evenement de  {self.event.nom_event}"


class ParticipationForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Add email field
    
    class Meta:
        model = participation
        fields = ['event', 'participan', 'date_inscription', 'phone_num', 'name_event']
        widgets = {
            'date_inscription': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'participan': forms.Select(attrs={'class': 'form-control'}),
        }





class paiement(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(evenement,null=True, on_delete=models.CASCADE)  
    participation = models.ForeignKey(participation, on_delete=models.CASCADE, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)  
    card_holder_name = models.CharField(max_length=200, blank=True, null=True)  
    expiry_date = models.DateField(blank=True, null=True)  
    cvv = models.CharField(max_length=3, blank=True, null=True) 
    payment_method = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Nouveau champ pour le montant


class Organisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organisateur")
    nom = models.CharField(max_length=200, default="")
    prenom = models.CharField(max_length=200, default="")
    email = models.EmailField(max_length=200, unique=True, default="")
    # description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"











class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")

def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user



class EvenementForm(forms.ModelForm):
    # Explicitly define image field to make it truly optional
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Image de l'événement (optionnel)"
    )
    
    class Meta:
        model = evenement
        # Exclude image_url since it's not in the database yet
        fields = ['nom_event', 'image', 'date', 'lieu', 'nombre_places', 'categorie', 'description', 'price']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'nombre_places': forms.NumberInput(attrs={'min': '2', 'class': 'form-control'}),
            'nom_event': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }
    
    def clean_nombre_places(self):
        nombre_places = self.cleaned_data.get('nombre_places')
        if nombre_places < 2:
            raise forms.ValidationError("Le nombre minimum de places doit être 2")
        return nombre_places




