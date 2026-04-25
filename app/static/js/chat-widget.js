(() => {
    const widget = document.getElementById("chat-widget");
    if (!widget) {
        return;
    }

    const endpoint = widget.dataset.endpoint;
    const toggle = document.getElementById("chat-toggle");
    const toggleIcon = document.getElementById("chat-toggle-icon");
    const card = document.getElementById("chat-card");
    const messages = document.getElementById("chat-messages");
    const input = document.getElementById("chat-input");
    const sendButton = document.getElementById("chat-send");
    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

    let isOpen = true;

    function addMessage(text, type) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${type}`;
        bubble.textContent = text;
        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
        return bubble;
    }

    async function sendMessage() {
        const message = input.value.trim();
        if (!message) {
            return;
        }

        addMessage(message, "user");
        input.value = "";
        input.disabled = true;
        sendButton.disabled = true;

        const loadingBubble = addMessage("Escrevendo resposta...", "loading");

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken ?? "",
                },
                body: JSON.stringify({ message }),
            });

            const payload = await response.json();
            loadingBubble.remove();

            if (!response.ok) {
                addMessage(
                    payload.reply || "Nao foi possivel responder agora.",
                    "ai",
                );
                return;
            }

            addMessage(payload.reply || "Sem resposta no momento.", "ai");
        } catch (error) {
            loadingBubble.remove();
            addMessage("Falha ao conectar com o assistente.", "ai");
            console.error("[chat-widget]", error);
        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
        }
    }

    toggle.addEventListener("click", () => {
        isOpen = !isOpen;
        card.hidden = !isOpen;
        toggle.setAttribute("aria-expanded", String(isOpen));
        toggleIcon.className = isOpen
            ? "fa-solid fa-chevron-down"
            : "fa-solid fa-chevron-up";
    });

    sendButton.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
})();
