"""Tests for the base DTA record"""
from unittest.mock import patch

from dta.records.record import DTARecord


@patch('dta.records.header.DTAHeader.validate')
def test_validate_header(mocker):
    """Verifies that the record validation triggers the header validation."""
    record = DTARecord()
    assert not mocker.called, "header validation should not be called before record validation is triggered"
    record.validate()
    assert mocker.call, "header validation should be called when record validation is triggered"
