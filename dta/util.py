"""Collection of utility functions"""
from string import whitespace


def remove_whitespace(text: str, whitespace_chars: str = whitespace) -> str:
    """Remove whitespace characters from a string.

    Args:
        text: The text to remove the whitespace from.
        whitespace_chars: The whitespace characters to remove from `text` (default: `string.whitespace`).

    Returns: A version of `text` without the characters defined in `whitespace_chars`
    """
    for char in whitespace_chars:
        if char in text:
            text = text.replace(char, '')
    return text


def is_swiss_iban(iban: str) -> bool:
    """Check if an IBAN is Swiss or not.

    Args:
        iban: the IBAN to check

    Returns: ``True`` if the IBAN is swiss, ``False`` otherwise.
    """
    return iban.country_code in ('CH', 'LI') if hasattr(iban, 'country_code') else iban.startswith(('CH', 'LI'))
