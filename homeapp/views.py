from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormRegistroUsuario, FormPerfil, FormEditarUser
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'homeapp/home.html')

def cursos(request):
    return render(request, 'homeapp/cursos.html')

def cadastro_usuario(request):
    if request.method == 'POST':
        form = FormRegistroUsuario(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Faça login para continuar.')
            return redirect('entrar') # Redireciona para a URL de login
    else:
        form = FormRegistroUsuario()
    return render(request, 'homeapp/cadastro_usuario.html', {'form': form})

@login_required
def editar_perfil(request):
    perfil = request.user.perfil
    user = request.user
    
    if request.method == 'POST':
        form_u = FormEditarUser(request.POST, instance=user)
        form_p = FormPerfil(request.POST, request.FILES, instance=perfil) # request.FILES para a foto
        
        if form_u.is_valid() and form_p.is_valid():
            form_u.save()
            form_p.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('home')
    else:
        form_u = FormEditarUser(instance=user)
        form_p = FormPerfil(instance=perfil)
        
    return render(request, 'homeapp/editar_perfil.html', {
        'form_u': form_u,
        'form_p': form_p
    })