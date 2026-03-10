from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .forms import FormRegistroUsuario, FormPerfil, FormEditarUser
from .models import Aula, Matricula, Presenca, Perfil, Turma, Curso, Nota

import io

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

@login_required
def painel_aluno(request):
    matriculas = Matricula.objects.filter(aluno=request.user.perfil)
    dados_cursos = []
    
    for m in matriculas:
        # Busca todas as aulas da turma para o cronograma
        aulas_turma = Aula.objects.filter(turma=m.turma).order_by('data')
        
        # Identifica quais aulas já tiveram chamada para este aluno
        aulas_com_chamada_ids = Presenca.objects.filter(
            matricula=m
        ).values_list('aula_id', flat=True)
        
        total_chamadas = aulas_com_chamada_ids.count()
        presencas = Presenca.objects.filter(matricula=m, presente=True).count()
        
        percentual = (presencas / total_chamadas * 100) if total_chamadas > 0 else 0
        
        dados_cursos.append({
            'matricula': m,
            'percentual_presenca': round(percentual, 1),
            'presencas_contagem': presencas,
            'total_aulas_ocorridas': total_chamadas,
            'faltas': total_chamadas - presencas,
            'notas': Nota.objects.filter(matricula=m),
            'aulas_cronograma': aulas_turma,
            'chamadas_realizadas_ids': aulas_com_chamada_ids,
        })
        
    return render(request, 'homeapp/painel_aluno.html', {'dados_cursos': dados_cursos})

@staff_member_required
def painel_admin_custom(request):
    # Estatísticas rápidas para o gestor
    context = {
        'total_alunos': Perfil.objects.filter(is_aluno=True).count(),
        'total_professores': Perfil.objects.filter(is_professor=True).count(),
        'cursos_ativos': Curso.objects.filter(status='P').count(),
        'turmas_andamento': Turma.objects.all().count(),
    }
    return render(request, 'homeapp/painel_admin.html', context)

@login_required
def detalhe_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id, status='P')
    turmas_disponiveis = Turma.objects.filter(
        curso=curso, 
        data_final__gte=timezone.now().date()
    )
    
    minhas_matriculas = Matricula.objects.filter(
        aluno=request.user.perfil
    ).values_list('turma_id', flat=True)

    if request.method == 'POST':
        # REGRA DE SEGURANÇA: Apenas perfis marcados como aluno podem se matricular
        if not request.user.perfil.is_aluno:
            messages.error(request, "Apenas alunos podem se matricular em turmas.")
            return redirect('detalhe_curso', curso_id=curso.id)

        turma_id = request.POST.get('turma_id')
        turma = get_object_or_404(Turma, id=turma_id)
        
        if turma.id in minhas_matriculas:
            messages.warning(request, "Você já está matriculado nesta turma.")
        else:
            Matricula.objects.create(aluno=request.user.perfil, turma=turma)
            messages.success(request, f"Matrícula realizada com sucesso!")
            return redirect('painel_aluno')

    return render(request, 'homeapp/detalhe_curso.html', {
        'curso': curso,
        'turmas': turmas_disponiveis,
        'minhas_matriculas': minhas_matriculas
    })

@login_required
def detalhe_turma_professor(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    
    # Validação de acesso do professor
    if not request.user.perfil.is_professor and not request.user.is_staff:
        messages.error(request, "Acesso restrito.")
        return redirect('home')

    # Processa o agendamento de nova aula
    if request.method == 'POST' and 'cadastrar_aula' in request.POST:
        data_aula = request.POST.get('data')
        anotacoes = request.POST.get('anotacoes')
        
        Aula.objects.create(turma=turma, data=data_aula, anotacoes=anotacoes)
        messages.success(request, f"Aula do dia {data_aula} agendada com sucesso!")
        return redirect('detalhe_turma_professor', turma_id=turma.id)

    aulas = Aula.objects.filter(turma=turma).order_by('-data')
    matriculas = Matricula.objects.filter(turma=turma, status='A')

    # Busca os IDs das aulas que já possuem ao menos um registro de presença
    aulas_com_chamada_ids = Presenca.objects.filter(
        aula__turma=turma
    ).values_list('aula_id', flat=True).distinct()

    return render(request, 'homeapp/detalhe_turma_professor.html', {
        'turma': turma,
        'aulas': aulas,
        'matriculas': matriculas,
        'aulas_com_chamada_ids': aulas_com_chamada_ids, # Enviado para o template
    })

@login_required
def lancar_nota(request, matricula_id):
    matricula = get_object_or_404(Matricula, id=matricula_id)
    
    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        
        # O uso de update_or_create impede notas duplicadas para a mesma unidade
        nota, created = Nota.objects.update_or_create(
            matricula=matricula,
            descricao_avaliacao=descricao,
            defaults={'valor': valor}
        )
        
        if created:
            messages.success(request, "Nota lançada com sucesso!")
        else:
            messages.info(request, "Nota atualizada com sucesso!")
            
        return redirect('detalhe_turma_professor', turma_id=matricula.turma.id)

    return render(request, 'homeapp/lancar_nota.html', {'matricula': matricula})

@login_required
def gerar_pdf_presenca(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Cabeçalho do PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Lista de Presença - EducApp")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Curso: {turma.curso.nome} | Turma: {turma.id}")
    p.drawString(100, 760, f"Professor: {turma.professor.user.get_full_name() if turma.professor else 'N/A'}")
    p.line(100, 750, 500, 750)

    # Listagem de Alunos
    y = 720
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y, "Nome do Aluno")
    p.drawString(400, y, "Assinatura / Presença")
    p.line(100, y-5, 500, y-5)
    
    y -= 25
    p.setFont("Helvetica", 10)
    for matricula in turma.matriculas.filter(status='A'):
        p.drawString(100, y, f"{matricula.aluno.user.get_full_name() or matricula.aluno.user.username}")
        p.line(380, y-2, 500, y-2) # Linha para assinatura
        y -= 20
        if y < 50: # Nova página se necessário
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'presenca_turma_{turma.id}.pdf')

@staff_member_required
def relatorio_certificados(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    # Filtra apenas os alunos cujo método 'situacao_detalhada' retorna algo que comece com 'Aprovado'
    alunos_aprovados = [m for m in turma.matriculas.all() if "Aprovado" in m.situacao_detalhada]
    
    return render(request, 'homeapp/relatorio_certificados.html', {
        'turma': turma,
        'aprovados': alunos_aprovados
    })

# Adicione esta nova função
@login_required
def gerar_pdf_desempenho(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, f"Relatório de Desempenho - {turma.curso.nome}")
    p.setFont("Helvetica", 10)
    p.drawString(100, 785, f"Professor: {turma.professor.user.get_full_name() if turma.professor else 'N/A'}")
    p.line(100, 775, 500, 775)

    y = 750
    # Cabeçalho da Tabela
    p.setFont("Helvetica-Bold", 9)
    p.drawString(100, y, "Aluno")
    p.drawString(250, y, "U1")
    p.drawString(280, y, "U2")
    p.drawString(310, y, "U3")
    p.drawString(340, y, "Final")
    p.drawString(380, y, "Média")
    p.drawString(430, y, "Situação")
    
    y -= 20
    p.setFont("Helvetica", 9)
    for m in turma.matriculas.all():
        n = m.notas_por_unidade
        p.drawString(100, y, f"{m.aluno.user.get_full_name()[:25]}")
        p.drawString(250, y, f"{n['u1'].valor if n['u1'] else '-'}")
        p.drawString(280, y, f"{n['u2'].valor if n['u2'] else '-'}")
        p.drawString(310, y, f"{n['u3'].valor if n['u3'] else '-'}")
        p.drawString(340, y, f"{n['final'].valor if n['final'] else '-'}")
        p.drawString(380, y, f"{m.media_atual}")
        p.drawString(430, y, f"{m.situacao_detalhada}")
        y -= 15
        if y < 50: p.showPage(); y = 800

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'desempenho_turma_{turma.id}.pdf')