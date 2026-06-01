(() => {
    'use strict';

    // ========================================================================
    // CONFIGURAÇÃO
    // ========================================================================

    const CONFIG = {
        MESSAGES: {
            EMPTY_TITLE: "Por favor, preencha o título/nome primeiro.",
            ELEMENTS_NOT_FOUND: "Erro: Não foi possível encontrar os campos necessários.",
            GENERIC_ERROR: "Erro ao gerar descrição. Tente novamente.",
            CONFIRM_DELETE: "Tem certeza que deseja remover?",
        },
    };

    // ========================================================================
    // UTILIDADES
    // ========================================================================

    /**
     * Obter token CSRF do meta tag
     */
    function getCsrfToken() {
        return document
            .querySelector('meta[name="csrf-token"]')
            ?.getAttribute("content") || "";
    }

    /**
     * Log estruturado para debug
     */
    function log(message, data = null) {
        console.log(`[dashboard.js] ${message}`, data || "");
    }

    // ========================================================================
    // CONFIRMAÇÃO DE EXCLUSÃO
    // ========================================================================

    function initConfirmDelete() {
        document.querySelectorAll(".js-confirm-form").forEach((form) => {
            form.addEventListener("submit", (event) => {
                const message = form.dataset.confirm || CONFIG.MESSAGES.CONFIRM_DELETE;
                if (!window.confirm(message)) {
                    event.preventDefault();
                }
            });
        });
        log("Confirmação de exclusão inicializada");
    }

    // ========================================================================
    // GERADOR DE DESCRIÇÃO
    // ========================================================================

    function initDescriptionGenerator() {
        const buttons = document.querySelectorAll(".js-ai-generate");

        if (buttons.length === 0) {
            log("Nenhum botão .js-ai-generate encontrado");
            return;
        }

        buttons.forEach((button) => {
            button.addEventListener("click", async (event) => {
                event.preventDefault();

                // ═══════════════════════════════════════════════════════════
                // 1. EXTRAIR DADOS DO BOTÃO
                // ═══════════════════════════════════════════════════════════

                const titleField = document.querySelector(button.dataset.source);
                const descriptionField = document.querySelector(button.dataset.target);
                const endpoint = button.dataset.endpoint;
                const type = button.dataset.type;

                // ═══════════════════════════════════════════════════════════
                // 2. VALIDAR ELEMENTOS
                // ═══════════════════════════════════════════════════════════

                if (!titleField || !descriptionField || !endpoint) {
                    console.error("[dashboard.js] Elementos não encontrados", {
                        source: button.dataset.source,
                        target: button.dataset.target,
                        endpoint,
                    });
                    window.alert(CONFIG.MESSAGES.ELEMENTS_NOT_FOUND);
                    return;
                }

                // ═══════════════════════════════════════════════════════════
                // 3. VALIDAR TÍTULO
                // ═══════════════════════════════════════════════════════════

                const title = titleField.value.trim();
                if (!title) {
                    window.alert(CONFIG.MESSAGES.EMPTY_TITLE);
                    titleField.focus();
                    return;
                }

                // ═══════════════════════════════════════════════════════════
                // 4. PREPARAR PARA REQUISIÇÃO
                // ═══════════════════════════════════════════════════════════

                button.disabled = true;
                const originalHTML = button.innerHTML;
                button.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Gerando...';

                try {
                    // ═════════════════════════════════════════════════════
                    // 5. FAZER REQUISIÇÃO AJAX
                    // ═════════════════════════════════════════════════════

                    log("Gerando descrição para:", { title, type });

                    const formData = new FormData();
                    formData.append("titulo", title);
                    formData.append("tipo", type);

                    const response = await fetch(endpoint, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCsrfToken(),
                        },
                        body: formData,
                    });

                    // ═════════════════════════════════════════════════════
                    // 6. PROCESSAR RESPOSTA
                    // ═════════════════════════════════════════════════════

                    const payload = await response.json();

                    if (!response.ok) {
                        throw new Error(
                            payload.error || CONFIG.MESSAGES.GENERIC_ERROR
                        );
                    }

                    // ═════════════════════════════════════════════════════
                    // 7. SUCESSO: PREENCHER CAMPO
                    // ═════════════════════════════════════════════════════

                    log("Descrição gerada com sucesso");
                    descriptionField.value = payload.description || "";
                    descriptionField.focus();

                    // ═════════════════════════════════════════════════════
                    // 8. FEEDBACK VISUAL
                    // ═════════════════════════════════════════════════════

                    button.innerHTML = '<i class="fa-solid fa-check"></i> Pronto!';
                    button.style.color = '#10b981'; // Verde

                    // Restaurar após delay
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                        button.style.color = '';
                        button.disabled = false;
                    }, 2000);

                } catch (error) {
                    // ═════════════════════════════════════════════════════
                    // 9. TRATAMENTO DE ERRO
                    // ═════════════════════════════════════════════════════

                    console.error("[dashboard.js] Erro ao gerar:", error);
                    window.alert(error.message || CONFIG.MESSAGES.GENERIC_ERROR);

                } finally {
                    // ═════════════════════════════════════════════════════
                    // 10. GARANTIR QUE BOTÃO É RESTAURADO
                    // ═════════════════════════════════════════════════════

                    if (button.disabled) {
                        button.disabled = false;
                        button.innerHTML = originalHTML;
                    }
                }
            });
        });

        log(`${buttons.length} botões de geração inicializados`);
    }

    // ========================================================================
    // INICIALIZAÇÃO GERAL
    // ========================================================================

    document.addEventListener("DOMContentLoaded", () => {
        log("Inicializando dashboard.js");
        initConfirmDelete();
        initDescriptionGenerator();
        log("Dashboard inicializado com sucesso");
    });

    // ========================================================================
    // DEBUG (opcional)
    // ========================================================================

    // Expor funções para debug no console
    if (window.location.hostname === "localhost") {
        window.DashboardDebug = {
            getCsrfToken,
            log,
            CONFIG,
        };
    }
})();
