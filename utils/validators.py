"""
utils/validators.py — Funciones de validación reutilizables.
"""

import ipaddress


def is_valid_cidr(cidr: str) -> bool:
    """Devuelve True si `cidr` es una dirección IP/prefijo válida."""
    try:
        ipaddress.ip_interface(cidr)
        return True
    except ValueError:
        return False


def is_valid_username(username: str) -> bool:
    """Solo letras, números y guión bajo."""
    return bool(username) and all(
        c.isalnum() or c == "_" for c in username
    )
