from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    foto = models.ImageField(upload_to='perfil_fotos/', null=True, blank=True)
    is_aluno = models.BooleanField(default=True)
    is_professor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} | {self.cpf}"

# Signal: Criar o Perfil automaticamente ao criar o User
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance, is_aluno=True)

# --- CURSOS E CONTEÚDO ---
class Curso(models.Model):
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('P', 'Publicado'),
        ('E', 'Encerrado'),
    ]
    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    carga_horaria = models.PositiveIntegerField(help_text="Carga horária em horas")
    descricao = models.TextField()
    data_lancamento = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='R')

    def __str__(self):
        return self.nome
    
# --- TURMAS E EXECUÇÃO ---
class Turma(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='turmas')
    professor = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_professor': True})
    dias_aula = models.CharField(max_length=100, help_text="Ex: Seg, Qua, Sex")
    data_inicio = models.DateField()
    data_final = models.DateField()

    def nome(self):
        return f"Turma {self.id} - {self.curso.nome}"

    def __str__(self):
        return f"Turma {self.id} {self.curso.nome} - Início: {self.data_inicio}"

class Aula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='aulas')
    data = models.DateField()
    anotacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Aula Id {self.id} - {self.data} - {self.turma.nome()}"

# --- RELACIONAMENTOS E ACADÊMICO ---
class Matricula(models.Model):
    STATUS_CHOICES = [
        ('A', 'Ativa'),
        ('C', 'Concluída'),
        ('T', 'Trancada'),
        ('D', 'Desistente'),
    ]
    aluno = models.ForeignKey(Perfil, on_delete=models.CASCADE, limit_choices_to={'is_aluno': True})
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='matriculas')
    data_matricula = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    class Meta:
        unique_together = ('aluno', 'turma')

    # REGRA DE NEGÓCIO: Cálculo de Média e Aprovação
    @property
    def notas_por_unidade(self):
        """Retorna um dicionário com as notas organizadas"""
        notas = self.notas.all()
        return {
            'u1': notas.filter(descricao_avaliacao='Unidade 1').first(),
            'u2': notas.filter(descricao_avaliacao='Unidade 2').first(),
            'u3': notas.filter(descricao_avaliacao='Unidade 3').first(),
            'final': notas.filter(descricao_avaliacao='Prova Final').first(),
        }

    @property
    def media_atual(self):
        n = self.notas_por_unidade
        notas_validas = [nota.valor for nota in [n['u1'], n['u2'], n['u3'], n['final']] if nota]
        if not notas_validas: return 0
        divisor = 4 if n['final'] else 3 # Regra da Prova Final
        return round(sum(notas_validas) / divisor, 1)

    @property
    def situacao_detalhada(self):
        n = self.notas_por_unidade
        # Lógica para turmas em andamento ou finalizadas
        if n['u1'] and n['u2'] and n['u3']:
            if self.media_atual >= 7.0: return "Aprovado"
            if n['final']:
                return "Aprovado (Pós-Final)" if self.media_atual >= 5.0 else "Reprovado"
            return "Na Recuperação / Aguardando Final"
        return "Cursando (Notas Parciais)"

    def __str__(self):
        return f"{self.aluno.user.username} - {self.turma}"

class Presenca(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    data_registro = models.DateField(auto_now_add=True)
    presente = models.BooleanField(default=True)

class Nota(models.Model):
    # Usando related_name='notas' para facilitar a busca na Matricula
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='notas')
    descricao_avaliacao = models.CharField(max_length=100) # Ex: Unidade 1, Prova Final
    valor = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    data_lancamento = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.descricao_avaliacao}: {self.valor} ({self.matricula.aluno.user.username})"

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pix'),
        ('B', 'Boleto'),
        ('C', 'Cartão'),
    ]
    aluno = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')