(() => {
    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

    document.querySelectorAll(".js-confirm-form").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirm || "Confirmar esta acao?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll(".js-ai-generate").forEach((button) => {
        button.addEventListener("click", async () => {
            const titleField = document.querySelector(button.dataset.source);
            const descriptionField = document.querySelector(button.dataset.target);
            const endpoint = button.dataset.endpoint;
            const type = button.dataset.type;

            if (!titleField || !descriptionField || !endpoint) {
                return;
            }

            const title = titleField.value.trim();
            if (!title) {
                titleField.focus();
                return;
            }

            button.disabled = true;
            const originalLabel = button.innerHTML;
            button.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Gerando...';

            try {
                const formData = new FormData();
                formData.append("titulo", title);
                formData.append("tipo", type);

                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken ?? "",
                    },
                    body: formData,
                });

                const payload = await response.json();
                if (!response.ok) {
                    throw new Error(payload.error || "Nao foi possivel gerar a descricao.");
                }

                descriptionField.value = payload.description || "";
                descriptionField.focus();
            } catch (error) {
                window.alert(error.message);
            } finally {
                button.disabled = false;
                button.innerHTML = originalLabel;
            }
        });
    });
})();
