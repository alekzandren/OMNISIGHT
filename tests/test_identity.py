"""
Tests for the identity processor module.
"""

import pytest
from unittest.mock import patch, AsyncMock
from modules.identity_processor import IdentityProcessor


class TestIdentityProcessor:
    """Test suite for IdentityProcessor."""

    @pytest.fixture
    def processor(self, data_handler):
        """IdentityProcessor fixture."""
        return IdentityProcessor(data_handler)

    def test_validate_passport_valid(self, processor):
        """Test passport validation with valid data."""
        valid_passports = [
            "1234 567890",
            "12 34 567890",
            "1234567890"
        ]

        for passport in valid_passports:
            result = processor.validate_passport(passport)
            assert result is True

    def test_validate_passport_invalid(self, processor):
        """Test passport validation with invalid data."""
        invalid_passports = [
            "1234 56789",  # Too short
            "1234 5678901",  # Too long
            "ABCD 567890",  # Contains letters
            "1234-567890",  # Wrong separator
            ""
        ]

        for passport in invalid_passports:
            result = processor.validate_passport(passport)
            assert result is False

    def test_validate_snils_valid(self, processor):
        """Test SNILS validation with valid data."""
        valid_snils = [
            "123-456-789 01",
            "12345678901"
        ]

        for snils in valid_snils:
            result = processor.validate_snils(snils)
            assert result is True

    def test_validate_snils_invalid(self, processor):
        """Test SNILS validation with invalid data."""
        invalid_snils = [
            "123-456-789 0",  # Too short
            "123-456-789 012",  # Too long
            "123-45-789 01",  # Wrong format
            "ABCD-456-789 01",  # Contains letters
            ""
        ]

        for snils in invalid_snils:
            result = processor.validate_snils(snils)
            assert result is False

    def test_validate_driver_license_valid(self, processor):
        """Test driver license validation with valid data."""
        valid_licenses = [
            "12AB345678",
            "1234AB567890",
            "123456789012"
        ]

        for license_num in valid_licenses:
            result = processor.validate_driver_license(license_num)
            assert result is True

    def test_validate_driver_license_invalid(self, processor):
        """Test driver license validation with invalid data."""
        invalid_licenses = [
            "12AB34567",  # Too short
            "12AB3456789",  # Too long
            "12-AB-345678",  # Wrong format
            ""
        ]

        for license_num in invalid_licenses:
            result = processor.validate_driver_license(license_num)
            assert result is False

    def test_process_identity_data_valid(self, processor):
        """Test processing valid identity data."""
        sample_data = {
            "full_name": "Иван Иванов",
            "passport": "1234 567890",
            "snils": "123-456-789 01",
            "driver_license": "12AB345678"
        }

        result = processor.process_identity_data(sample_data)

        assert result["full_name"] == sample_data["full_name"]
        assert result["passport"]["valid"] is True
        assert result["snils"]["valid"] is True
        assert result["driver_license"]["valid"] is True

    @pytest.mark.asyncio
    async def test_search_identity_leaks(self, processor):
        """Test searching for identity data in leak databases."""
        sample_data = {
            "full_name": "Иван Иванов",
            "passport": "1234 567890",
            "snils": "123-456-789 01",
            "driver_license": "12AB345678"
        }

        with patch('modules.identity_processor.IdentityProcessor._search_leak_database',
                   new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"source": "leak1", "data": "passport:1234 567890"},
                {"source": "leak2", "data": "snils:123-456-789 01"}
            ]

            result = await processor.search_identity_leaks(sample_data)

            assert len(result) == 2
            assert result[0]["source"] == "leak1"
            assert result[1]["source"] == "leak2"
            mock_search.assert_called_once()