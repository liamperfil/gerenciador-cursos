from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormRegistroUsuario
from django.contrib.auth import authenticate, login

# Create your views here.
def home(request):
    return render(request, 'homeapp/home.html')

def cursos(request):
    return render(request, 'homeapp/cursos.html')

def entrar(request):
    if request.method == 'POST':
        usuario_post = request.POST.get('username')
        senha_post = request.POST.get('password')
        user = authenticate(request, username=usuario_post, password=senha_post)
        if user is not None:
            login(request, user)
            return redirect('home') # Ou para a página de login.html que você criou
    return render(request, 'homeapp/entrar.html')

def cadastro_usuario(request):
    if request.method == 'POST':
        form = FormRegistroUsuario(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Faça login para continuar.')
            return redirect('login') # Redireciona para a URL de login
    else:
        form = FormRegistroUsuario()
    return render(request, 'homeapp/cadastro_usuario.html', {'form': form})
