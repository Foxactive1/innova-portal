# 🔴 RELATÓRIO DE DIAGNÓSTICO — InNovaIdeia Portal

## PROBLEMAS IDENTIFICADOS

### 1️⃣ **GROQ_API_KEY não está configurada**
```
Status: ✗ NÃO ENCONTRADA
Impacto: Chat 503 + Geração de IA quebrada
```

**Por que acontece:**
- Em `ai.py:33`, `get_groq_client()` verifica `current_app.config.get("GROQ_API_KEY")`
- Se não encontrar, retorna `None`
- Depois, em `_completion()`, lança `AIUnavailableError("Integracao de IA indisponivel.")`
- Que é capturada em `routes.py` e retorna HTTP 503

**Cadeia de erro:**
```
routes.py /api/chat
  ↓ generate_chat_reply()
    ↓ ai.py _completion()
      ↓ get_groq_client() → None
        ↓ raise AIUnavailableError
          ↓ RETURN 503
```

---

### 2️⃣ **Falta de logging detalhado**
Atualmente, exceções são genéricas:
```python
except Exception as exc:
    raise AIServiceError("Falha ao consultar o provedor de IA.") from exc
```

❌ Isso **esconde o erro real** (autenticação, rate limit, modelo inválido, etc)

---

### 3️⃣ **Sem fallback para testes**
Sem `GROQ_API_KEY`, toda geração de IA falha (esperado, mas sem teste possível)

---

## SOLUÇÃO (3 PASSOS)

### ✅ PASSO 1: Configurar GROQ_API_KEY
Adicione em seu `config.py` ou `.env`:
```python
GROQ_API_KEY = "seu-api-key-aqui"  # Obter em https://console.groq.com
GROQ_MODEL = "mixtral-8x7b-32768"  # ou outro modelo disponível
```

### ✅ PASSO 2: Melhorar ai.py com logging
Vou fornecer uma versão corrigida que:
- Registra erros específicos (RateLimitError, AuthenticationError, etc)
- Fornece mensagens mais úteis
- Tem fallback para desenvolvimento

### ✅ PASSO 3: Testar conexão Groq
Antes de usar em routes, validar a chave

---

## PRÓXIMOS PASSOS
1. Você vai fornecer sua `GROQ_API_KEY`? (para teste)
2. Quer um fallback mock para desenvolvimento?
3. Quer melhorar o logging também?

