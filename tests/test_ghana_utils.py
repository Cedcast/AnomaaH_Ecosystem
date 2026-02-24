"""Test suite for Ghana-specific utilities."""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.ghana_utils import validate_ghana_phone

def test_valid_ghana_phone():
    """Test validation of valid Ghana phone numbers."""
    result = validate_ghana_phone("+233244123456")
    assert result['valid'] is True
    assert result['network'] == 'MTN'

def test_invalid_ghana_phone():
    """Test validation of invalid phone numbers."""
    result = validate_ghana_phone("123456")
    assert result['valid'] is False
