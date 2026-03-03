from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    
    # Papéis
    is_aluno = models.BooleanField(default=True) # Já começa como True
    is_professor = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.username}"

# Signal: Criar o Perfil automaticamente ao criar o User
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance, is_aluno=True)