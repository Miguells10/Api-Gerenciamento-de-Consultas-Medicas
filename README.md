# API Gerenciamento de Consultas Médicas

> API RESTful para gerenciamento de profissionais de saúde e consultas médicas, com impacto social.

---

## 📋 Sobre o Projeto

Esta API foi desenvolvida com **Python + Django + Django REST Framework (DRF)**, seguindo boas práticas de arquitetura limpa, segurança e testabilidade. Permite o gerenciamento completo de profissionais de saúde e consultas médicas, com autenticação JWT e documentação interativa Swagger.

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python 3.12 | Linguagem principal |
| Django 5.1 | Framework web |
| Django REST Framework | Construção da API REST |
| djangorestframework-simplejwt | Autenticação JWT |
| django-cors-headers | Configuração de CORS |
| django-filter | Filtragem de endpoints |
| drf-spectacular | Documentação OpenAPI/Swagger |
| PostgreSQL 15 | Banco de dados |
| Poetry | Gerenciamento de dependências |
| Docker + Docker Compose | Containerização |
| Gunicorn | Servidor WSGI de Produção |
| Ruff | Linting e Formatação (Padrão 2025) |
| GitHub Actions | CI/CD |

---

## 🌐 Link de Acesso (Live API)

O projeto está implantado na **AWS EC2** com deploy automatizado:

- **Swagger UI (Documentação):** [https://54.205.4.26/api/docs/](https://54.205.4.26/api/docs/)
- **API Host:** `https://54.205.4.26`

> [!IMPORTANT]
> A API utiliza certificados SSL e autenticação JWT. Para testar os endpoints via Swagger, obtenha o token no endpoint `/api/v1/auth/token/`.

---

## ✅ Pré-requisitos

- [Python 3.12+](https://python.org)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker + Docker Compose](https://docs.docker.com/compose/install/) *(opcional)*

---

## 🚀 Instalação Local (sem Docker)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/api-gerenciamento-consultas-medicas.git
cd api-gerenciamento-consultas-medicas
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com seus valores
```

### 3. Instale as dependências

```bash
poetry install
```

### 4. Execute as migrações

```bash
poetry run python manage.py migrate
```

### 5. Crie um superusuário (para acessar o admin e obter tokens JWT)

```bash
poetry run python manage.py createsuperuser
```

### 6. Inicie o servidor de desenvolvimento

```bash
poetry run python manage.py runserver
```

A API estará disponível em `http://localhost:8000`.

---

## 🐳 Execução com Docker

### 1. Configure o arquivo `.env`

```bash
cp .env.example .env
# Edite o .env conforme necessário
```

### 2. Suba os containers

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8000`. O container utiliza **Gunicorn** com **3 workers** para garantir alta performance e concorrência no atendimento das requisições.

### 3. Crie um superusuário (em outro terminal)

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🔑 Autenticação JWT

Todos os endpoints (exceto `/api/docs/`) requerem autenticação via **Bearer Token**.

### Obter token de acesso

```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

### Renovar token

```bash
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ..."
}
```

### Usar o token nas requisições

```bash
Authorization: Bearer <access_token>
```

---

## ⚠️ Padronização de Respostas de Erro

A API utiliza um handler customizado para garantir que **todos** os erros (400, 401, 404, 500) retornem uma estrutura JSON consistente, facilitando o consumo pelo frontend:

```json
{
  "status": "error",
  "message": "Descrição detalhada do erro",
  "code": "NomeDaExcecao (ex: ValidationError)"
}
```

---

## 📡 Endpoints da API

### Profissionais de Saúde

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v1/professionals/` | Listar todos os profissionais |
| `POST` | `/api/v1/professionals/` | Cadastrar novo profissional |
| `GET` | `/api/v1/professionals/{id}/` | Detalhar profissional |
| `PUT` | `/api/v1/professionals/{id}/` | Atualizar profissional (completo) |
| `PATCH` | `/api/v1/professionals/{id}/` | Atualizar profissional (parcial) |
| `DELETE` | `/api/v1/professionals/{id}/` | Remover profissional |

**Exemplo de payload (POST/PUT):**
```json
{
  "social_name": "Dra. Ana Lima",
  "profession": "Cardiologista",
  "address": "Rua das Flores, 123, São Paulo - SP",
  "contact": "+5511999999999"
}
```

### Consultas Médicas

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v1/appointments/` | Listar todas as consultas |
| `GET` | `/api/v1/appointments/?professional={id}` | **Filtrar por profissional** |
| `POST` | `/api/v1/appointments/` | Agendar nova consulta |
| `GET` | `/api/v1/appointments/{id}/` | Detalhar consulta |
| `PATCH` | `/api/v1/appointments/{id}/` | Atualizar consulta (ex: status) |
| `DELETE` | `/api/v1/appointments/{id}/` | Cancelar consulta |

**Exemplo de payload (POST):**
```json
{
  "professional": "uuid-do-profissional",
  "date": "2026-04-15T10:00:00-03:00"
}
```

**Status disponíveis:** `SCHEDULED`, `COMPLETED`, `CANCELED`

---

## 📖 Documentação Interativa (Swagger)

Após iniciar o servidor, acesse:

- **Swagger UI:** `http://localhost:8000/api/docs/`
- **Schema OpenAPI (JSON):** `http://localhost:8000/api/schema/`

---

## 🧪 Testes

### Executar todos os testes

```bash
# Local (com Poetry)
poetry run python manage.py test --verbosity=2

# Docker
docker compose run --rm web python manage.py test --verbosity=2

# Lint e Formatação (Ruff)
uv run ruff check .   # Verificar erros
uv run ruff check . --fix  # Corrigir automaticamente
poetry run ruff check .      # Verificar erros
poetry run ruff check --fix . # Corrigir erros automaticamente
poetry run ruff format .     # Ajustar formatação (estilo Black)
```

> **Nota:** Todos os testes automatizados utilizam **tokens JWT reais** via `setUp`, simulando fielmente o comportamento de produção.

### Executar com cobertura de código

```bash
poetry run coverage run manage.py test
poetry run coverage report
poetry run coverage html  # Gera relatório HTML em htmlcov/
```

---

## 🏛 Justificativas Técnicas

| Decisão | Justificativa |
|---|---|
| **Django + DRF** | Iteração rápida, ORM robusto, proteção nativa contra SQLi/CSRF e ecossistema maduro |
| **JWT (stateless)** | Facilita escalabilidade horizontal no AWS; funciona para web e mobile |
| **UUID como PK** | Previne enumeração de IDs e ataques de IDOR |
| **PROTECT no FK** | Evita deletar profissionais com consultas ativas acidentalmente |
| **`select_related`** | Previne queries N+1 nas listagens de consultas |
| **Poetry** | Builds determinísticos, lock file garante paridade dev/produção |
| **Gunicorn** | Servidor WSGI profissional com 3 workers simultâneos (escalabilidade) |
| **Standardized Errors** | Melhora a DX (Developer Experience) e facilita o tratamento no frontend |
| **Clean Code** | Código sem comentários redundantes e seguindo padrões de estilo modernos |
| **Docker multi-stage** | Imagem de produção enxuta sem dependências de build |
| **Blue/Green deploy** | Rollback instantâneo sem downtime |
| **Testes com JWT Real** | Testes simulam o fluxo completo de autenticação Bearer, garantindo alinhamento com a segurança real da API |
| **Configuração Local-First** | `settings.py` prioriza execução local (`localhost`), com overrides automáticos no `docker-compose` para garantir portabilidade total |

---

### 📦 GitHub Secrets Sugeridas

Para o funcionamento do pipeline de deploy, configure as seguintes Secrets no repositório:

| Secret | Descrição |
|---|---|
| `EC2_HOST` | IP ou Host do servidor (Staging/Prod) |
| `EC2_USERNAME` | Usuário SSH (ex: ubuntu) |
| `EC2_SSH_KEY` | Chave privada SSH (.pem) |
| `POSTGRES_DB` | Nome do banco de dados |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `SECRET_KEY` | Django Secret Key |

---

## 🔄 Estratégia de Rollback

O pipeline de CI/CD foi desenhado para facilitar a recuperação em caso de erros:

1. **Rollback Automático**: Caso o deploy falhe ou o container não suba (erro no `docker compose up`), o script de deploy interrompe a execução.
2. **Rollback Manual**: Para voltar a uma versão anterior que estava estável:
   - Acesse o **GitHub Actions**.
   - Selecione a "Run" de um commit que você sabe que estava funcionando.
   - Clique em **Re-run all jobs** (isso fará o deploy daquela versão específica novamente sobre a atual).
3. **Persistência**: Como os dados do PostgreSQL estão em um volume Docker, o rollback do código não afeta a integridade das consultas já cadastradas (a menos que haja uma incompatibilidade crítica de schema).

---

## 💳 Integração Asaas (Arquitetura — Bônus)

A integração com o **Asaas** para split de pagamentos segue este fluxo:

```
Paciente paga consulta
    │
    ▼
Django API → Asaas API (cria cobrança com split)
    │
    ├── Plataforma recebe: % de taxa de serviço
    └── Profissional recebe: % restante (wallet do Asaas)

Asaas envia webhook → POST /api/v1/webhooks/asaas/
    └── Django atualiza status da consulta para PAID
```

**Endpoint webhook** (protegido por token Asaas, sem JWT):
```
POST /api/v1/webhooks/asaas/
X-Asaas-Token: <token_secreto_do_asaas>
```

---

## 📁 Estrutura do Projeto

```
api-gerenciamento-consultas-medicas/
├── config/             # Configurações Django
├── apps/
│   ├── core/           # Modelos base e Exception Handler
│   ├── professionals/  # CRUD profissionais
│   ├── appointments/   # CRUD consultas
│   └── auth/           # JWT endpoints
├── .github/workflows/  # CI/CD GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```
