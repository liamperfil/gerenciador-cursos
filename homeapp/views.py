from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import FormRegistroUsuario, FormPerfil, FormEditarUser
from django.contrib.auth.decorators import login_required
from .models import Aula, Matricula, Presenca, Perfil, Turma, Curso

# Create your views here.
def home(request):
    return render(request, 'homeapp/home.html')

def cursos(request):
    # Captura o valor da busca vindo da URL (ex: ?busca=python)
    termo_busca = request.GET.get('busca')
    
    # Busca apenas cursos publicados por padrão
    todos_cursos = Curso.objects.filter(status='P')
    
    if termo_busca:
        # Filtra cursos cujo nome contenha o termo (case-insensitive)
        todos_cursos = todos_cursos.filter(nome__icontains=termo_busca)
    
    return render(request, 'homeapp/cursos.html', {'cursos': todos_cursos})

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

def realizar_chamada(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    # Buscamos apenas matrículas ativas da turma
    matriculas = Matricula.objects.filter(turma=aula.turma, status='A')
    
    if request.method == 'POST':
        # Pegamos a lista de IDs de matrículas que foram marcadas como presentes
        presentes_ids = request.POST.getlist('alunos_presentes')
        
        for matricula in matriculas:
            # Atualiza ou cria o registro de presença para cada aluno
            Presenca.objects.update_or_create(
                aula=aula,
                matricula=matricula,
                defaults={'presente': str(matricula.id) in presentes_ids}
            )
        
        messages.success(request, f"Chamada da aula {aula.data} realizada com sucesso!")
        return redirect('home') # Ou para o detalhe da turma

    # Verifica quem já tem presença marcada para carregar o checkbox preenchido
    presencas_atuais = Presenca.objects.filter(aula=aula, presente=True).values_list('matricula_id', flat=True)
    
    return render(request, 'homeapp/realizar_chamada.html', {
        'aula': aula,
        'matriculas': matriculas,
        'presencas_atuais': presencas_atuais
    })

@login_required
def painel_professor(request):
    # Verifica se o usuário tem perfil de professor
    if not request.user.perfil.is_professor:
        messages.error(request, "Acesso restrito a professores.")
        return redirect('home')
    
    # Busca turmas onde este perfil é o professor
    turmas = Turma.objects.filter(professor=request.user.perfil)
    
    return render(request, 'homeapp/painel_professor.html', {'turmas': turmas})