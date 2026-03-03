from django.contrib import admin
from .models import Perfil, Curso, Aula, Turma, Matricula, Presenca, Nota, Pagamento

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
    list_display = ('curso', 'professor', 'data_inicio')
    list_filter = ('curso', 'professor')

# Registro simples para as demais entidades
admin.site.register(Aula)
admin.site.register(Matricula)
admin.site.register(Presenca)
admin.site.register(Nota)
admin.site.register(Pagamento)