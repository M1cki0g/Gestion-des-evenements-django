from pyexpat.errors import messages
from django.shortcuts import render,HttpResponse
# from .models import evenement
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .models import CustomUserCreationForm  # Importez le formulaire personnalisé
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_superuser:
                    return redirect(reverse('mon_dashboard'))
                else:
                    login(request, user)
                    return redirect('home')
        
        # Afficher l'erreur ici directement, peu importe la raison
        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})



# @staff_member_required
# def dashboard(request):
#         return render(request, 'dashboard.html')





def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if not form.is_valid():
            # Si le formulaire est invalide, renvoyer les erreurs sous chaque champ
            return render(request, 'signup.html', {'form': form})

        user = form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(request, username=username, password=password)

        if user is None:
            # Si l'utilisateur ne peut pas être authentifié, renvoyer sans message d'erreur
            return render(request, 'signup.html', {'form': form})

        login(request, user)
        
        return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})





def logout_view(request):
    if request.method == 'POST':
        django_logout(request)
        return redirect('home')  # Assure-toi que l'URL "home" existe bien
    return render(request, 'home.html')


@login_required
def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"Message de {name} via Contact Us"
        full_message = f"Nom : {name}\nEmail : {email}\n\nMessage :\n{message}"

        try:
            # Envoyer l'email
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,  # L'email de l'expéditeur
                ['yassinetouli35@gmail.com'],  # L'email de destination
                fail_silently=False,
            )
            messages.success(request, "Votre message a été envoyé avec succès.")
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite : {str(e)}")

        return redirect('home')  # Redirige vers la page d'accueil après l'envoi

    return render(request, 'home.html')








