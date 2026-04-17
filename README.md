# 🚀 InNovaIdeia – Plataforma de Serviços e Produtos em Tecnologia

**InNovaIdeia** é uma aplicação web desenvolvida com Flask que oferece uma vitrine para serviços e produtos de tecnologia, com sistema de captação de leads, painel administrativo e autenticação de usuários. Ideal para empresas de consultoria, desenvolvimento de software, IA e automação.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Funcionalidades

- ✅ Página inicial dinâmica com **serviços** e **produtos** cadastrados no banco de dados
- ✅ Formulário de **contato** (leads) com armazenamento no banco
- ✅ **Autenticação** de usuários (login/registro/logout) com senhas hasheadas
- ✅ **Dashboard administrativo** protegido por login:
  - Adicionar/remover serviços
  - Adicionar/remover produtos
  - Visualizar todos os leads recebidos
- ✅ Banco de dados SQLite (pronto para migrar para PostgreSQL/MySQL)
- ✅ Interface moderna com **Bootstrap 5** + CSS customizado (efeito vidro, cards animados, gradientes)
- ✅ Mensagens flash de feedback para o usuário
- ✅ Tratamento de erros e proteção de rotas

---

## 🛠️ Tecnologias utilizadas

| Camada          | Tecnologia                               |
|----------------|------------------------------------------|
| Backend        | Python 3, Flask, Flask-SQLAlchemy        |
| Autenticação   | Werkzeug (hash de senhas), sessões Flask |
| Frontend       | HTML5, Bootstrap 5, CSS customizado      |
| Banco de dados | SQLite (desenvolvimento)                 |
| Controle de versão | Git + GitHub                         |

---

## 📁 Estrutura do projeto
innova_portal/
├── app/
│ ├── init.py # Fábrica da aplicação Flask
│ ├── models.py # Modelos User, Lead, Service, Product
│ ├── database.py # Instância do SQLAlchemy
│ ├── routes.py # Rotas principais (home, dashboard, contato)
│ ├── auth.py # Rotas de autenticação
│ ├── utils.py # Decorator login_required
│ ├── populate.py # Script para popular banco com dados iniciais
│ ├── static/
│ │ └── css/
│ │ └── style.css # Estilos personalizados
│ └── templates/
│ ├── base.html # Template base (navbar, flash messages)
│ ├── index.html # Página inicial (serviços, produtos, contato)
│ ├── dashboard.html # Painel administrativo
│ ├── login.html
│ └── register.html
├── database.db # Arquivo do SQLite (criado automaticamente)
├── requirements.txt
└── README.md

text

---

## 🚀 Como executar o projeto localmente

### Pré-requisitos

- Python 3.9 ou superior instalado
- Git (opcional, para clonar)

### Passo a passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/innova-portal.git
   cd innova-portal
Crie e ative um ambiente virtual

bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
Instale as dependências

bash
pip install -r requirements.txt
Popule o banco de dados com dados iniciais (opcional, mas recomendado)

bash
python -m app.populate
Isso criará 5 serviços e 3 produtos de exemplo.

Execute a aplicação

bash
# Modo desenvolvimento (com recarga automática)
flask --app app run --debug
# Ou
python -m flask --app app run
Acesse no navegador

text
http://127.0.0.1:5000
Crie um usuário administrador
Acesse /register e cadastre-se. Depois faça login em /login para acessar o dashboard.

🧪 Script de população (populate.py)
O script populate.py insere dados iniciais de serviços e produtos, evitando duplicatas.
Execute sempre que quiser restaurar os dados padrão (desde que as tabelas existam).

bash
python -m app.populate
🔒 Segurança e boas práticas implementadas
Senhas armazenadas com generate_password_hash

Rotas administrativas protegidas por login_required

Uso de flash() para feedback imediato

Tratamento de exceções nas operações de banco de dados (try/except com rollback)

Separação de blueprints (main e auth)

Configuração de SECRET_KEY via variável de ambiente (recomendado para produção)

📸 Capturas de tela
Página Inicial	Dashboard
https://via.placeholder.com/400x200?text=Home+InNovaIdeia	https://via.placeholder.com/400x200?text=Dashboard
Substitua os placeholders por imagens reais do seu projeto hospedadas em Imgur ou na própria pasta /screenshots.

🧰 Possíveis melhorias futuras
Adicionar paginação na lista de leads

Edição de serviços/produtos diretamente no dashboard

Envio de e-mail automático após contato

Gráficos de leads por período

Suporte a múltiplos idiomas (i18n)

Testes automatizados (pytest)

Dockerização da aplicação

🤝 Contribuição
Contribuições são muito bem-vindas! Siga os passos:

Faça um fork do projeto

Crie uma branch para sua feature (git checkout -b feature/nova-feature)

Commit suas mudanças (git commit -m 'Adiciona nova feature')

Push para a branch (git push origin feature/nova-feature)

Abra um Pull Request

📄 Licença
Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para mais informações.

✒️ Autor
Dione Castro Alves
GitHub • LinkedIn

🙏 Agradecimentos
Bootstrap 5 pela base visual

Flask e sua comunidade

Todos os colaboradores e clientes que inspiraram este projeto

Desenvolvido com 💜 para o ecossistema de inovação e tecnologia.
