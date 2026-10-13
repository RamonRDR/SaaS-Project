"""Validação isolada do marcador deste experimento."""


def is_valid_wakeup(message: str) -> bool:
    """Aceita apenas o conteúdo completo e exato autorizado para o canary."""
    return message == "MODE_A_DEV_CANARY_TEST_20261013"
