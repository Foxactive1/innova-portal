(() => {
    const form = document.getElementById("contact-form");
    const submitButton = document.getElementById("contact-submit");

    if (!form || !submitButton) {
        return;
    }

    form.addEventListener("submit", () => {
        submitButton.disabled = true;
        submitButton.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Enviando...';
    });
})();
