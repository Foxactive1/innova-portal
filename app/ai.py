from __future__ import annotations

import logging
from flask import current_app, g

from .models import Product, Service

# Configurar logger para IA
logger = logging.getLogger(__name__)


class AIServiceError(RuntimeError):
    """Erro genérico de serviço de IA (problema na API/rede)."""
    pass


class AIUnavailableError(AIServiceError):
    """IA indisponível (sem chave configurada ou limite atingido)."""
    pass


class AIAuthenticationError(AIServiceError):
    """Erro de autenticação com a API Groq."""
    pass


def get_groq_client():
    """
    Obter ou criar cliente Groq singleton por request.

    Retorna None se GROQ_API_KEY não estiver configurada.
    """
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        logger.warning(
            "[InNovaIdeia] GROQ_API_KEY não configurada. "
            "IA indisponível. Configure em .env ou config.py"
        )
        return None

    # Singleton por request (flask g context)
    client = getattr(g, "_groq_client", None)
    if client is None:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            g._groq_client = client
            logger.info("[InNovaIdeia] Cliente Groq inicializado com sucesso.")
        except ImportError:
            logger.error(
                "[InNovaIdeia] Biblioteca 'groq' não instalada. "
                "Execute: pip install groq"
            )
            raise AIServiceError(
                "Biblioteca Groq não instalada. Execute 'pip install groq'."
            ) from None
        except Exception as exc:
            logger.exception("[InNovaIdeia] Erro ao inicializar cliente Groq.")
            raise AIServiceError(f"Erro ao inicializar Groq: {exc}") from exc

    return client


def detect_intent(message):
    """Detectar intenção do usuário pela mensagem."""
    msg = (message or "").lower()
    if any(keyword in msg for keyword in ("preco", "preço", "valor", "quanto custa")):
        return "pricing"
    if any(keyword in msg for keyword in ("crm", "sistema", "plataforma", "saas")):
        return "product_interest"
    if any(keyword in msg for keyword in ("automacao", "automação", "bot", "whatsapp")):
        return "automation"
    if any(keyword in msg for keyword in ("site", "landing page", "pagina", "página")):
        return "web_dev"
    return "general"


def _catalog_context():
    """Gerar contexto com catálogo de serviços e produtos."""
    services = Service.query.order_by(Service.titulo.asc()).limit(8).all()
    products = Product.query.order_by(Product.nome.asc()).limit(8).all()

    services_text = "\n".join(
        f"- {service.titulo}: {service.descricao[:180]}" for service in services
    ) or "- Nenhum servico publico cadastrado."

    products_text = "\n".join(
        f"- {product.nome} ({product.display_price}): {product.descricao[:180]}"
        for product in products
    ) or "- Nenhum produto publico cadastrado."

    return services_text, products_text


def _completion(messages, temperature, max_tokens):
    """
    Chamar Groq API para completar mensagens.

    Retorna: str (conteúdo da resposta)
    Levanta: AIUnavailableError, AIAuthenticationError, AIServiceError
    """
    client = get_groq_client()
    if not client:
        raise AIUnavailableError(
            "Integracao de IA indisponivel. Configure GROQ_API_KEY."
        )

    model = current_app.config.get("GROQ_MODEL", "mixtral-8x7b-32768")

    try:
        logger.debug(
            f"[Groq] Chamando {model} com temp={temperature}, "
            f"max_tokens={max_tokens}, messages={len(messages)}"
        )

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content.strip()
        logger.debug(f"[Groq] Resposta recebida ({len(content)} chars)")
        return content

    except ImportError as exc:
        logger.error("[Groq] Biblioteca groq não instalada.")
        raise AIServiceError("Groq não instalado. pip install groq") from exc

    except Exception as exc:
        exc_type = type(exc).__name__
        exc_msg = str(exc)

        # Diagnosticar tipo específico de erro
        if "RateLimitError" in exc_type or "rate limit" in exc_msg.lower():
            logger.warning(f"[Groq] Rate limit atingido: {exc_msg}")
            raise AIUnavailableError(
                "Limite de requisições atingido. Tente novamente em instantes."
            ) from exc

        elif "AuthenticationError" in exc_type or "401" in exc_msg:
            logger.error(f"[Groq] Erro de autenticação: {exc_msg}")
            raise AIAuthenticationError(
                "GROQ_API_KEY inválida ou expirada."
            ) from exc

        elif "ConnectionError" in exc_type or "timeout" in exc_msg.lower():
            logger.error(f"[Groq] Erro de conexão: {exc_msg}")
            raise AIUnavailableError(
                "Servico de IA indisponivel momentaneamente."
            ) from exc

        else:
            logger.exception(f"[Groq] Erro desconhecido ({exc_type}): {exc_msg}")
            raise AIServiceError(
                f"Erro ao consultar IA: {exc_type}"
            ) from exc


# ============================================================================
# FUNÇÕES PÚBLICAS (usadas em routes.py)
# ============================================================================

def classify_lead(message):
    """
    Classificar lead usando Groq.

    Retorna: str no formato "Classificacao: X | Sugestao: Y"
    """
    services_text, products_text = _catalog_context()
    system_prompt = (
        "Voce classifica leads para uma consultoria de tecnologia. "
        "Analise somente a mensagem recebida e use o catalogo publico informado. "
        "Responda em uma unica linha no formato: "
        "'Classificacao: X | Sugestao: Y'."
    )
    user_prompt = (
        "Catalogo publico:\n"
        f"Servicos:\n{services_text}\n\n"
        f"Produtos:\n{products_text}\n\n"
        f"Mensagem do lead:\n{message}"
    )

    try:
        return _completion(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=120,
        )
    except AIServiceError as exc:
        logger.error(f"[classify_lead] {exc}")
        raise


def generate_chat_reply(message):
    """
    Gerar resposta de chat contextualizada.

    Retorna: tuple (reply: str, intent: str)
    """
    services_text, products_text = _catalog_context()
    intent = detect_intent(message)

    system_prompt = f"""
Voce e um consultor comercial da InNovaIdeia.

Catalogo publico de servicos:
{services_text}

Catalogo publico de produtos:
{products_text}

Intencao principal detectada: {intent}

Regras:
- use apenas o catalogo publico acima
- nunca cite leads, operacoes internas ou dados sensiveis
- nao invente servicos nem precos
- responda em portugues do Brasil
- seja objetivo, consultivo e orientado a conversao
""".strip()

    try:
        reply = _completion(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.5,
            max_tokens=320,
        )
        return reply, intent
    except AIServiceError as exc:
        logger.error(f"[generate_chat_reply] {exc}")
        raise


def generate_marketing_description(title, item_type):
    """
    Gerar descricao de marketing para servico/produto.

    Retorna: str (descricao)
    """
    type_label = "servico" if item_type == "service" else "produto"
    prompt = (
        f"Crie uma descricao profissional para um {type_label} chamado '{title}'. "
        "Use um unico paragrafo com no maximo 90 palavras, linguagem clara, "
        "tom premium e foco em resultado para o cliente."
    )

    try:
        return _completion(
            [{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=160,
        )
    except AIServiceError as exc:
        logger.error(f"[generate_marketing_description] {exc}")
        raise


def generate_weekly_summary(leads):
    """
    Gerar resumo semanal de leads.

    Retorna: str (resumo executivo)
    """
    if not leads:
        raise ValueError("Nao ha leads suficientes para gerar resumo.")

    lead_block = "\n".join(
        f"- {lead.nome} ({lead.email}): {lead.mensagem[:220]}" for lead in leads
    )
    prompt = (
        "Voce esta escrevendo um resumo executivo semanal para uma consultoria de "
        "tecnologia. A partir dos leads abaixo, entregue:\n"
        "1. Principais dores recorrentes\n"
        "2. Oportunidades comerciais\n"
        "3. Recomendacoes operacionais imediatas\n"
        "4. Proximos passos sugeridos\n\n"
        f"Leads:\n{lead_block}"
    )

    try:
        return _completion(
            [{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=700,
        )
    except AIServiceError as exc:
        logger.error(f"[generate_weekly_summary] {exc}")
        raise