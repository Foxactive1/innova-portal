# 🚀 GUIA: Corrigir Chat 503 + Geração de IA — InNovaIdeia Portal

## 📋 RESUMO DO PROBLEMA

| Sintoma | Causa | Solução |
|---------|-------|--------|
| `POST /api/chat` retorna 503 | `GROQ_API_KEY` não configurada | Configurar credenciais |
| Geração de descrição falha | Falta de modelo Groq | Configurar `GROQ_MODEL` |
| Sem logs de erro | Exceções genéricas | Usar `ai_improved.py` |

---

## ✅ PASSO 1: Obter sua GROQ_API_KEY

1. Visite: **https://console.groq.com**
2. Faça login ou crie conta
3. Vá em **API Keys**
4. Copie sua chave (começa com `gsk_`)
5. Guarde seguro (não compartilhe!)

**Exemplo:**
```
gsk_XyZ1a2B3c4D5e6F7g8H9i0J1k2L3m4N5
```

---

## ✅ PASSO 2: Configurar Variáveis de Ambiente

### **Opção A: Arquivo `.env` (recomendado)**

1. Na raiz do seu projeto, crie arquivo `.env`:
```bash
touch .env
```

2. Adicione:
```env
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXx  # Cole sua chave aqui
GROQ_MODEL=mixtral-8x7b-32768
FLASK_SECRET_KEY=sua-chave-secreta-muito-longa-aqui
```

3. Certifique-se que seu `config.py` carrega `.env`:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Carregar .env

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-change-in-production")
    # ... resto das configs
```

### **Opção B: Direto em `config.py`** (apenas para desenvolvimento)

```python
class Config:
    GROQ_API_KEY = "gsk_XXXXXXXXXXXXXXXXXx"  # Cole aqui
    GROQ_MODEL = "mixtral-8x7b-32768"
    # ... resto
```

---

## ✅ PASSO 3: Substituir `ai.py` pela versão melhorada

1. **Backup da versão anterior:**
```bash
cp app/ai.py app/ai.py.backup
```

2. **Copiar novo arquivo:**
```bash
# Arquivo: ai_improved.py → app/ai.py
cp ai_improved.py app/ai.py
```

3. **Nenhuma mudança necessária em `routes.py`** (API compatível)

---

## 🧪 PASSO 4: Testar a Configuração

### **Teste Rápido no Terminal**

```bash
python
```

```python
import os
from dotenv import load_dotenv
load_dotenv()

# Verificar
api_key = os.getenv("GROQ_API_KEY")
print(f"✓ API_KEY encontrada: {api_key[:10]}...") if api_key else print("✗ API_KEY não encontrada")

# Testar conexão
from groq import Groq

client = Groq(api_key=api_key)
response = client.chat.completions.create(
    model="mixtral-8x7b-32768",
    messages=[{"role": "user", "content": "Diga OK"}],
    max_tokens=5,
    temperature=0.1
)
print(f"✓ Groq conectado: {response.choices[0].message.content}")
```

**Saída esperada:**
```
✓ API_KEY encontrada: gsk_XXX...
✓ Groq conectado: OK
```

---

## 🔍 PASSO 5: Testar no App

1. **Reiniciar Flask:**
```bash
python -m flask run
```

2. **Teste #1: Chat Widget**
   - Abra http://localhost:5000
   - Envie mensagem no chat
   - Verificar resposta (não mais 503)

3. **Teste #2: Gerar Descrição**
   - Faça login (http://localhost:5000/login)
   - Dashboard → "Adicionar Serviço"
   - Clique "Gerar com IA"
   - Verificar descrição gerada

4. **Teste #3: Resumo Semanal**
   - Dashboard → "Resumo Semanal"
   - Deve gerar sem erros

---

## 📊 VERIFICAR LOGS

Agora com `ai_improved.py`, você terá logs detalhados:

```python
# Adicione em seu app.py ou config:
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Logs esperados:**
```
[Groq] Chamando mixtral-8x7b-32768 com temp=0.5, max_tokens=320
[Groq] Resposta recebida (156 chars)
```

---

## ❌ TROUBLESHOOTING

| Erro | Causa | Solução |
|------|-------|--------|
| `AIUnavailableError: GROQ_API_KEY não configurada` | Falta `.env` ou `GROQ_API_KEY` | Criar `.env` com credenciais |
| `AuthenticationError: 401` | API_KEY inválida | Copiar novamente de console.groq.com |
| `RateLimitError` | Limite de requisições atingido | Esperar 1 min ou usar modelo mais rápido |
| `Biblioteca groq não instalada` | Falta pip install | `pip install groq` |
| `ModuleNotFoundError: dotenv` | Falta python-dotenv | `pip install python-dotenv` |

---

## 📝 RESUMO DOS ARQUIVOS

```
innova_portal/
├── config.py              ← Adicione load_dotenv() e GROQ_API_KEY
├── .env                   ← NOVO: Variáveis de ambiente (NÃO commit!)
├── app/
│   ├── ai.py             ← SUBSTITUIR por ai_improved.py
│   ├── routes.py         ← Sem mudanças necessárias
│   ├── auth.py           ← Sem mudanças
│   └── models.py         ← Sem mudanças
```

---

## ✨ RESULTADO FINAL

Depois de aplicar estes passos:

✅ Chat widget retorna respostas (não mais 503)
✅ Geração de descrição funciona
✅ Resumo semanal gera insights
✅ Logs detalhados mostram o que está acontecendo
✅ Erros são informativos (não genéricos)

---

## 🔐 SEGURANÇA

⚠️ **IMPORTANTE:**
- Nunca compartilhe seu `GROQ_API_KEY`
- Adicione `.env` ao `.gitignore`
- Use chaves diferentes para dev/prod
- Rotacione chaves regularmente

```bash
# .gitignore
.env
.env.local
*.pyc
__pycache__/
```

---

**Dúvidas?** Teste os passos acima. Se algo quebrar, me avise com o erro exato! 🚀
