(() => {
    const passwordInput = document.getElementById("register-password");
    const confirmInput = document.getElementById("register-password-confirm");
    const meterFill = document.getElementById("password-meter-fill");
    const meterLabel = document.getElementById("password-meter-label");
    const matchStatus = document.getElementById("password-match-status");
    const form = document.getElementById("register-form");
    const submitButton = document.getElementById("register-submit");

    if (!passwordInput || !confirmInput || !meterFill || !meterLabel || !matchStatus || !form) {
        return;
    }

    function passwordScore(password) {
        let score = 0;
        if (password.length >= 8) score += 35;
        if (password.length >= 12) score += 15;
        if (/[A-Z]/.test(password)) score += 15;
        if (/[0-9]/.test(password)) score += 15;
        if (/[^A-Za-z0-9]/.test(password)) score += 20;
        return Math.min(score, 100);
    }

    function updateStrength() {
        const score = passwordScore(passwordInput.value);
        meterFill.style.width = `${score}%`;

        if (score < 40) {
            meterFill.style.background = "#f97373";
            meterLabel.textContent = "Senha fraca";
        } else if (score < 70) {
            meterFill.style.background = "#f5b942";
            meterLabel.textContent = "Senha media";
        } else {
            meterFill.style.background = "#18b27f";
            meterLabel.textContent = "Senha forte";
        }
    }

    function passwordsMatch() {
        if (!confirmInput.value) {
            matchStatus.textContent = "Repita a senha para confirmar.";
            return true;
        }

        const matches = passwordInput.value === confirmInput.value;
        matchStatus.textContent = matches
            ? "As senhas coincidem."
            : "As senhas nao coincidem.";
        return matches;
    }

    passwordInput.addEventListener("input", () => {
        updateStrength();
        passwordsMatch();
    });

    confirmInput.addEventListener("input", passwordsMatch);

    form.addEventListener("submit", (event) => {
        if (!passwordsMatch()) {
            event.preventDefault();
            confirmInput.focus();
            return;
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Criando conta...';
        }
    });
})();
