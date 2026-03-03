from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class FormRegistroUsuario(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class FormEditarUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class FormPerfil(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['cpf', 'data_nascimento', 'bio', 'foto']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se o CPF já existe, desabilita o campo para não permitir alteração
        if self.instance and self.instance.cpf:
            self.fields['cpf'].disabled = True
            self.fields['data_nascimento'].disabled = True