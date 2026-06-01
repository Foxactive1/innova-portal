"""
Módulo de inteligência artificial – arquitetura desacoplada (corrigida).
"""

from __future__ import annotations

import logging
from flask import current_app, g

from .models import Product, Service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceções
# ---------------------------------------------------------------------------

class AIServiceError(RuntimeError):
    """Erro genérico de serviço de IA (problema na API/rede)."""
    pass

class AIUnavailableError(AIServiceError):
    """IA indisponível (sem chave configurada ou limite atingido)."""
    pass

class AIAuthenticationError(AIServiceError):
    """Erro de autenticação com a API Groq."""
    pass

# ---------------------------------------------------------------------------
# Catálogo público
# ---------------------------------------------------------------------------

def _catalog_context():
    services = Service.query.order_by(Service.titulo.asc()).limit(8).all()
    products = Product.query.order_by(Product.nome.asc()).limit(8).all()

    services_text = "\n".join(
        f"- {s.titulo}: {s.descricao[:180]}" for s in services
    ) or "- Nenhum serviço público cadastrado."

    products_text = "\n".join(
        f"- {p.nome} ({p.display_price}): {p.descricao[:180]}"
        for p in products
    ) or "- Nenhum produto público cadastrado."

    return services_text, products_text

# ---------------------------------------------------------------------------
# 1. GroqProvider – não depende de current_app no construtor
# ---------------------------------------------------------------------------

class GroqProvider:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key
        self.model = model or "llama-3.3-70b-versatile"

    def _get_client(self):
        if not self.api_key:
            raise AIUnavailableError("GROQ_API_KEY não configurada.")
        client = getattr(g, "_groq_client", None)
        if client is None:
            try:
                from groq import Groq
                client = Groq(api_key=self.api_key)
                g._groq_client = client
                logger.info("Cliente Groq inicializado.")
            except ImportError:
                raise AIServiceError("Biblioteca 'groq' não instalada.") from None
            except Exception as exc:
                raise AIServiceError(f"Erro ao inicializar Groq: {exc}") from exc
        return client

    def complete(self, messages, temperature=0.5, max_tokens=320):
        client = self._get_client()
        try:
            logger.debug("Chamando Groq model=%s", self.model)
            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = resp.choices[0].message.content.strip()
            logger.debug("Resposta Groq (%d caracteres)", len(content))
            return content
        except Exception as exc:
            exc_name = type(exc).__name__
            msg = str(exc)
            if "RateLimitError" in exc_name or "rate limit" in msg.lower():
                raise AIUnavailableError("Limite de requisições atingido.") from exc
            if "AuthenticationError" in exc_name or "401" in msg:
                raise AIAuthenticationError("GROQ_API_KEY inválida.") from exc
            if "ConnectionError" in exc_name or "timeout" in msg.lower():
                raise AIUnavailableError("Serviço de IA indisponível.") from exc
            logger.exception("Erro Groq (%s): %s", exc_name, msg)
            raise AIServiceError(f"Erro na IA: {exc_name}") from exc

# ---------------------------------------------------------------------------
# 2. IntentEngine
# ---------------------------------------------------------------------------

class IntentEngine:
    KEYWORDS = [
        (("preco", "preço", "valor", "quanto custa"), "pricing"),
        (("crm", "sistema", "plataforma", "saas"), "product_interest"),
        (("automacao", "automação", "bot", "whatsapp"), "automation"),
        (("site", "landing page", "pagina", "página"), "web_dev"),
    ]

    def detect(self, message: str) -> str:
        msg = (message or "").lower()
        for keywords, intent in self.KEYWORDS:
            if any(kw in msg for kw in keywords):
                return intent
        return "general"

# ---------------------------------------------------------------------------
# 3. PromptBuilder
# ---------------------------------------------------------------------------

class PromptBuilder:
    @staticmethod
    def classification_prompt(message: str) -> list[dict]:
        services_text, products_text = _catalog_context()
        system = (
            "Você classifica leads para uma consultoria de tecnologia. "
            "Responda em uma única linha: 'Classificacao: X | Sugestao: Y'."
        )
        user = (
            "Catálogo público:\n"
            f"Serviços:\n{services_text}\n\n"
            f"Produtos:\n{products_text}\n\n"
            f"Mensagem do lead:\n{message}"
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    @staticmethod
    def chat_prompt(message: str, intent: str) -> list[dict]:
        services_text, products_text = _catalog_context()
        system = (
            "Você é um consultor comercial da InNovaIdeia.\n\n"
            f"Catálogo público de serviços:\n{services_text}\n\n"
            f"Catálogo público de produtos:\n{products_text}\n\n"
            f"Intenção detectada: {intent}\n\n"
            "Regras:\n- use apenas o catálogo público\n"
            "- nunca cite leads ou dados sensíveis\n"
            "- responda em português do Brasil\n"
            "- seja objetivo e consultivo"
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ]

    @staticmethod
    def marketing_prompt(title: str, type_label: str) -> list[dict]:
        user = (
            f"Crie uma descrição profissional para um {type_label} chamado '{title}'. "
            "Use um único parágrafo com no máximo 90 palavras, linguagem clara, "
            "tom premium e foco em resultado para o cliente."
        )
        return [{"role": "user", "content": user}]

    @staticmethod
    def weekly_summary_prompt(leads) -> list[dict]:
        lead_block = "\n".join(
            f"- {lead.nome} ({lead.email}): {lead.mensagem[:220]}" for lead in leads
        )
        user = (
            "Escreva um resumo executivo semanal para uma consultoria de tecnologia "
            "com base nos leads abaixo. Entregue:\n"
            "1. Principais dores recorrentes\n"
            "2. Oportunidades comerciais\n"
            "3. Recomendações operacionais imediatas\n"
            "4. Próximos passos sugeridos\n\n"
            f"Leads:\n{lead_block}"
        )
        return [{"role": "user", "content": user}]

# ---------------------------------------------------------------------------
# 4. LeadScoringEngine
# ---------------------------------------------------------------------------

class LeadScoringEngine:
    def __init__(self, groq_provider: GroqProvider, prompt_builder: PromptBuilder):
        self.groq = groq_provider
        self.prompt_builder = prompt_builder

    def classify(self, message: str) -> str:
        messages = self.prompt_builder.classification_prompt(message)
        return self.groq.complete(messages, temperature=0.2, max_tokens=120)

# ---------------------------------------------------------------------------
# 5. MemoryService (placeholder)
# ---------------------------------------------------------------------------

class MemoryService:
    def load_context(self, lead_id=None):
        return ""

    def save_turn(self, lead_id, role, message):
        pass

# ---------------------------------------------------------------------------
# 6. FallbackResponses
# ---------------------------------------------------------------------------

class FallbackResponses:
    @staticmethod
    def classification():
        return "Classificacao automatica indisponivel no momento."

    @staticmethod
    def chat():
        return "Assistente de IA indisponível no momento."

    @staticmethod
    def marketing():
        return "Descrição gerada automaticamente indisponível."

    @staticmethod
    def weekly_summary():
        return "Resumo semanal indisponível no momento."

# ---------------------------------------------------------------------------
# 7. AIOrchestrator – recebe api_key e model explicitamente
# ---------------------------------------------------------------------------

class AIOrchestrator:
    def __init__(
        self,
        groq_provider: GroqProvider | None = None,
        api_key: str | None = None,
        model: str | None = None,
        intent_engine: IntentEngine | None = None,
        prompt_builder: PromptBuilder | None = None,
        lead_scoring: LeadScoringEngine | None = None,
        memory: MemoryService | None = None,
        fallback: FallbackResponses | None = None,
    ):
        # Se receber um GroqProvider já instanciado, usa; senão cria um com as configs
        self.groq = groq_provider if groq_provider else GroqProvider(api_key=api_key, model=model)
        self.intent = intent_engine or IntentEngine()
        self.prompts = prompt_builder or PromptBuilder()
        self.scoring = lead_scoring or LeadScoringEngine(self.groq, self.prompts)
        self.memory = memory or MemoryService()
        self.fallback = fallback or FallbackResponses()

    def classify_lead(self, message: str) -> str:
        try:
            return self.scoring.classify(message)
        except AIUnavailableError:
            logger.info("Groq indisponível para classificar lead.")
            return self.fallback.classification()
        except AIServiceError:
            logger.exception("Falha ao classificar lead.")
            return self.fallback.classification()

    def generate_chat_reply(self, message: str) -> tuple[str, str]:
        intent = self.intent.detect(message)
        try:
            messages = self.prompts.chat_prompt(message, intent)
            reply = self.groq.complete(messages, temperature=0.5, max_tokens=320)
            return reply, intent
        except AIUnavailableError:
            return self.fallback.chat(), intent
        except AIServiceError:
            logger.exception("Falha no chat público.")
            return self.fallback.chat(), intent

    def generate_marketing_description(self, title: str, item_type: str) -> str:
        type_label = "serviço" if item_type == "service" else "produto"
        try:
            messages = self.prompts.marketing_prompt(title, type_label)
            return self.groq.complete(messages, temperature=0.6, max_tokens=160)
        except AIUnavailableError:
            return self.fallback.marketing()
        except AIServiceError:
            logger.exception("Falha ao gerar descrição.")
            return self.fallback.marketing()

    def generate_weekly_summary(self, leads) -> str:
        if not leads:
            raise ValueError("Nenhum lead para gerar resumo.")
        try:
            messages = self.prompts.weekly_summary_prompt(leads)
            return self.groq.complete(messages, temperature=0.4, max_tokens=700)
        except AIUnavailableError:
            return self.fallback.weekly_summary()
        except AIServiceError:
            logger.exception("Falha ao gerar resumo semanal.")
            return self.fallback.weekly_summary()


# ---------------------------------------------------------------------------
# Funções de integração com a aplicação Flask
# ---------------------------------------------------------------------------

def init_ai(app):
    """Inicializa e registra o AIOrchestrator na extensão Flask."""
    api_key = app.config.get("GROQ_API_KEY")
    model = app.config.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    app.extensions["ai"] = AIOrchestrator(api_key=api_key, model=model)
    logger.info("AIOrchestrator inicializado com sucesso.")


def get_ai() -> AIOrchestrator:
    """Recupera o AIOrchestrator registrado na aplicação Flask."""
    if "ai" not in current_app.extensions:
        raise RuntimeError("AIOrchestrator não foi inicializado. Chame init_ai(app).")
    return current_app.extensions["ai"]