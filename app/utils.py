from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from email_validator import EmailNotValidError, validate_email

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


def clamp_text(value, max_length):
    return (value or "").strip()[:max_length]


def validate_username(username):
    normalized = clamp_text(username, 30)
    if not normalized:
        raise ValueError("Informe um nome de usuario.")
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Use de 3 a 30 caracteres com letras, numeros, ponto, hifen ou underscore."
        )
    return normalized


def validate_email_address(email):
    candidate = (email or "").strip()
    if not candidate:
        raise ValueError("Informe um e-mail.")

    try:
        validated = validate_email(candidate, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError("Informe um e-mail valido.") from exc

    return validated.normalized


def parse_price(value):
    raw_value = (value or "").strip().replace(",", ".")
    if not raw_value:
        raise ValueError("Informe um preco.")

    try:
        amount = Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValueError("Preco invalido. Use um numero positivo.") from exc

    if amount < 0:
        raise ValueError("Preco invalido. Use um numero positivo.")

    return float(amount.quantize(Decimal("0.01")))
