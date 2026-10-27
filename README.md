# 🤖 Familia OS - Agente IA (FastAPI)

Serviço isolado de Inteligência Artificial para o ecossistema **Familia OS**, desenvolvido com **FastAPI**, **LangChain** e **Google Gemini**.

## 🎯 Funcionalidades

1. **OCR Inteligente de Cupons Fiscais (Visão Computacional):**
   - Extrai automaticamente fornecedor, data, valor total e itens discriminados (com quantidade e valor unitário) a partir de fotos de comprovantes fiscais.
   - Endpoint: `POST /api/ocr/receipt`

2. **Consultas em Linguagem Natural (Text-to-SQL):**
   - Agente conversacional que responde a perguntas da família sobre localização de itens, garantias, histórico de manutenções e rotinas consultando o schema `familialm` no Supabase.
   - Endpoint: `POST /api/chat`

---

## 🛠️ Como Executar Localmente

### 1. Criar e ativar o ambiente virtual (Python 3.10+)

No Windows (PowerShell):
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar as dependências

```powershell
pip install -r requirements.txt
```

### 3. Configurar as variáveis de ambiente

Copie o `.env.example` para `.env`:
```powershell
cp .env.example .env
```
Preencha com sua `GOOGLE_API_KEY` (Gemini) e a `SUPABASE_DB_URL` (String de conexão direta com o PostgreSQL do Supabase).

### 4. Iniciar a API

```powershell
uvicorn app.main:app --reload --port 8000
```

A documentação interativa estará acessível em: `http://localhost:8000/docs`

---

## 🐳 Execução via Docker

A imagem é gerada e publicada automaticamente no Docker Hub pelo pipeline de CI/CD:

```bash
docker pull <usuario>/familia-os-ai:latest
docker run -d -p 8000:8000 --name familia-os-ai \
  -e GOOGLE_API_KEY="sua_chave" \
  -e SUPABASE_DB_URL="postgresql://postgres:postgres@host:54322/postgres" \
  <usuario>/familia-os-ai:latest
```
