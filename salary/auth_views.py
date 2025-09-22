from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .auth_forms import CustomLoginForm, ChangePasswordForm
from .models import User

def login_view(request):
    """Vue de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Vérifier si l'utilisateur doit changer son mot de passe
            if user.must_change_password:
                messages.warning(request, 
                    "⚠️ Vous devez changer votre mot de passe avant de continuer.")
                return redirect('salary_auth:change_password')
            
            messages.success(request, f"✅ Bienvenue, {user.first_name or user.email} !")
            return redirect('index')
    else:
        form = CustomLoginForm()
    
    return render(request, 'salary/auth/login.html', {'form': form})

@login_required
def change_password_view(request):
    """Vue de changement de mot de passe obligatoire"""
    if not request.user.must_change_password:
        return redirect('index')
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.must_change_password = False
            user.save()
            messages.success(request, 
                "✅ Votre mot de passe a été changé avec succès !")
            return redirect('index')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'salary/auth/change_password.html', {
        'form': form,
        'user': request.user
    })

def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, "👋 Vous avez été déconnecté avec succès.")
    return redirect('salary_auth:login')

def send_user_credentials(user, temporary_password, request=None):
    """Envoie les identifiants temporaires par email"""
    subject = "🔐 Vos identifiants de connexion - Système de Paie"
    
    # URL de connexion par défaut
    login_url = '/auth/login/'
    if request:
        login_url = request.build_absolute_uri('/auth/login/')
    
    context = {
        'user': user,
        'temporary_password': temporary_password,
        'login_url': login_url,
        'site_name': 'Système de Paie Guinée'
    }
    
    html_message = render_to_string('salary/emails/user_credentials.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False
