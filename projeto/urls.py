"""
URL configuration for projeto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from homeapp import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Páginas Públicas
    path('', views.home, name='home'),
    path('cursos/', views.cursos, name='cursos'),
    path('curso/<int:curso_id>/', views.detalhe_curso, name='detalhe_curso'),

    # Autenticação e Perfil
    path('entrar/', auth_views.LoginView.as_view(template_name='homeapp/entrar.html'), name='entrar'),
    path('entrar/cadastrar/', views.cadastro_usuario, name='cadastro_usuario'),
    path('sair/', auth_views.LogoutView.as_view(next_page='home'), name='sair'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # Painéis de Controle
    path('aluno/painel/', views.painel_aluno, name='painel_aluno'),
    path('professor/painel/', views.painel_professor, name='painel_professor'),
    path('admin/painel/', views.painel_admin_custom, name='painel_admin_custom'),

    # Gestão Acadêmica (Professor)
    path('aula/<int:aula_id>/chamada/', views.realizar_chamada, name='realizar_chamada'),
    path('professor/lancar-nota/<int:matricula_id>/', views.lancar_nota, name='lancar_nota'),
    path('professor/turma/<int:turma_id>/', views.detalhe_turma_professor, name='detalhe_turma_professor'),
    path('professor/turma/<int:turma_id>/pdf/', views.gerar_pdf_presenca, name='gerar_pdf_presenca'),
    path('professor/turma/<int:turma_id>/pdf-desempenho/', views.gerar_pdf_desempenho, name='gerar_pdf_desempenho'),

    # Django Admin System
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)