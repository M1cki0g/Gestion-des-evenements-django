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
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional external image URL")
    date = models.DateTimeField()
    lieu = models.CharField(max_length=200)
    nombre_places = models.IntegerField(default=2)
    categorie = models.CharField(max_length=200)
    description = models.TextField(max_length=2000 , blank=True, null=True)
    organisateur = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
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
        exclude = ['organisateur', 'organisateur_name', 'is_validated', 'nombre_participants']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'nombre_places': forms.NumberInput(attrs={'min': '2', 'class': 'form-control'}),
            'nom_event': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def clean_nombre_places(self):
        nombre_places = self.cleaned_data.get('nombre_places')
        if nombre_places < 2:
            raise forms.ValidationError("Le nombre minimum de places doit être 2")
        return nombre_places
        
    def clean(self):
        # Custom validation to handle the complete form
        cleaned_data = super().clean()
        # We'll accept either an image file or an image URL
        if not cleaned_data.get('image') and not cleaned_data.get('image_url'):
            # It's okay to have neither - we'll use a default
            pass
        return cleaned_data




