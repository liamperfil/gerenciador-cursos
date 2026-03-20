# EducApp - Gerenciador de Cursos

Este aplicativo está sendo desenvolvido por alunos como parte das atividades do Programa Bolsa Futuro Digital (Back-End Python), iniciativa do Ministério da Ciência, Tecnologia e Inovação, realizado pelo CEPEDI sob a orientação do professor **Pedro Kislansky**.

O que fizemos até aqui é um gerenciador de cursos. Nosso objetivo é criar uma plataforma definitiva de gestão acadêmica para a rede pública de ensino da Bahia. Integrar professores, alunos e a família, oferecendo recursos que vão desde o acompanhamento de frequência em tempo real até a geração de relatórios de desempenho e listas de presença em PDF. A solução atende a uma demanda real: reduzir o abismo digital entre a rede pública e privada, proporcionando aos pais o portal do aluno, recurso já consolidado no ensino particular, mas ainda escasso na rede estadual.

---

## Tecnologias e Bibliotecas

### **Principal**
* **Python**: Linguagem de programação utilizada no ambiente de desenvolvimento.
* **Django**: Framework principal utilizado para toda a lógica de negócio, rotas e segurança.
* **SQLite3**: Banco de dados relacional nativo.

### **Bibliotecas Essenciais**
Utilizamos três das bibliotecas citadas nas apresentações do dia 06/12/2025.
* **Pillow**: Processamento de imagens utilizado para o upload e tratamento das fotos de perfil de usuários.
* **ReportLab**: Biblioteca para a criação dinâmica de documentos PDF (Listas de Presença e Desempenho).
* **Requests**: Utilizada para o consumo seguro de dados externos das APIs.

### **Front-end e UX**
* **Inspiração**: https://www.escolavirtual.gov.br
* **Bootstrap 5.3**: Framework CSS para garantir uma interface responsiva e moderna.
* **Construtor Bootstrap**: https://bootstrap.build/app
* **CSS Customizado**: Implementação de efeitos de *glassmorphism* na navbar e botões com comportamento *hover* inverso.

---

## Integração com APIs

* [BrasilAPI - Feriados](https://brasilapi.com.br/docs#tag/Feriados-Nacionais) para fornecer um calendário dinâmico de feriados nacionais na página de notícias.
* [AwesomeAPI - Cotações](https://docs.awesomeapi.com.br/api-de-moedas) para exibir cotação de euro, dólar e bitcoin.

---

## Funcionalidades de Destaque

* **Regras de Negócio Rígidas**: O sistema impede o lançamento da "Prova Final" caso as unidades U1, U2 e U3 não estejam preenchidas no banco de dados.
* **Cálculo de Média Inteligente**: Lógica personalizada no modelo de Matrícula que diferencia médias regulares de situações pós-recuperação.
* **Notificações Automáticas**: Envio de e-mail ao aluno via console (SMTP não configurado) sempre que uma nova nota é registrada pelo professor.
* **Diário de Classe Visual**: Interface que altera o estado visual (cores e ícones) automaticamente após a conclusão da chamada.
* **Painéis Segmentados**: Áreas exclusivas para Alunos (desempenho), Professores (gestão de turmas) e Gestores (estatísticas gerais).

---

## O que foi exigido pelo orientador
* Mínimo de 7 telas ✅ (home, cursos, cadastro, login, notícias, painel aluno, detalhe turma, +)
* Entrada no sistema via login e senha criptografada ✅ (para isso utilizamos Django Auth, sistema integrado do framework, utilizando formulário independente ao invés de usar o formulário django admin)
* Cadastro com inserção de dados, exclusão, e alteração de dados ✅ (presente principalmente na página de edição de perfil do usuário)
* Notificação via e-mail ✅ (envio de email de notificação (no console), notifica ao lançar nota do aluno, ver arquivo settings.py)
* Consumo de pelo menos 2 Api's externas ✅ (BrasilAPI Feriados e AwesomeAPI Cotações)
* Pelo menos uma tela de relatório (tabela dinâmica) ✅ (relatório de desempenho do aluno e +)
* 1 tela de dashboard ✅ (painel do gestor)

---

## Como Executar o Projeto

1. **Clone o repositório**: 
   ```bash
   git clone https://github.com/liamperfil/gerenciador-cursos.git

2. **Crie e ative seu ambiente virtual**:
    ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt

4. Execute as migrações:
    ```bash
    python manage.py migrate

5. Inicie o servidor:
    ```bash
    python manage.py runserver

© 2026 Jean Lima - Salvador, BA.