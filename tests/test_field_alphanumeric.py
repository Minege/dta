"""Tests for the Alphanumeric field"""
import pytest  # pylint: disable=import-error

from dta.fields import AlphaNumeric
from dta.records.record import DTARecord

FIELD_LENGTH = 10


class ANRecord(DTARecord):
    """Subclass of DTARecord for testing the Alphanumeric field"""
    field = AlphaNumeric(length=FIELD_LENGTH, truncate=False)


@pytest.mark.parametrize(('input_text', 'expected_text'), (
    ('Bob', 'Bob'),
    ('Zürich', 'Zuerich'),
    ('Était', 'Etait')
))
def test_characters_conversion(input_text, expected_text):
    """Verifies that text is converted correctly"""
    expected_text = expected_text.ljust(10, ' ')
    record = ANRecord()
    record.field = input_text
    assert record.field == expected_text
