from django.contrib import admin
from .models import Perfil, Curso, Aula, Turma, Matricula, Presenca, Nota, Pagamento
from django.urls import reverse
from django.utils.html import format_html

# Configuração para exibir o Perfil com filtros de papel (Aluno/Professor)
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'is_aluno', 'is_professor')
    list_filter = ('is_aluno', 'is_professor')
    search_fields = ('user__username', 'cpf')

# Configuração de Cursos
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'carga_horaria', 'status', 'data_lancamento')
    list_filter = ('status', 'categoria')
    search_fields = ('nome',)

# Configuração de Turmas vinculadas ao Professor
@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'curso', 'professor', 'data_inicio')
    list_filter = ('curso', 'professor')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'status', 'data_matricula')
    list_filter = ('status', 'turma')
    search_fields = ('aluno__user__username', 'turma__curso__nome')

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('aula', 'get_aluno', 'presente')
    list_filter = ('aula__turma', 'presente')

    def get_aluno(self, obj):
        return obj.matricula.aluno
    get_aluno.short_description = 'Aluno'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Esta lógica filtra os alunos no dropdown de 'Matrícula' 
        para exibir apenas quem pertence à turma daquela aula.
        """
        if db_field.name == "matricula":
            # Tenta pegar o ID da aula se você estiver editando uma
            aula_id = request.resolver_match.kwargs.get('object_id')
            if aula_id:
                aula = Aula.objects.get(pk=aula_id)
                kwargs["queryset"] = Matricula.objects.filter(turma=aula.turma, status='A')
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('data', 'turma', 'link_chamada')
    
    def link_chamada(self, obj):
        url = reverse('realizar_chamada', args=[obj.pk])
        return format_html('<a href="{}">Fazer Chamada</a>', url)
    
    link_chamada.short_description = 'Ação'

# Registro simples para as demais entidades
admin.site.register(Nota)
admin.site.register(Pagamento)