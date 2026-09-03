"""
Tests for the network analyzer module.
"""

import pytest
from unittest.mock import patch, AsyncMock
from modules.network_analyzer import NetworkAnalyzer


class TestNetworkAnalyzer:
    """Test suite for NetworkAnalyzer."""

    @pytest.fixture
    def analyzer(self, data_handler):
        """NetworkAnalyzer fixture."""
        return NetworkAnalyzer(data_handler)

    def test_validate_email_valid(self, analyzer):
        """Test email validation with valid data."""
        valid_emails = [
            "user@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]

        for email in valid_emails:
            result = analyzer.validate_email(email)
            assert result is True

    def test_validate_email_invalid(self, analyzer):
        """Test email validation with invalid data."""
        invalid_emails = [
            "user@example",  # Missing TLD
            "@example.com",  # Missing local part
            "user@",  # Missing domain
            "user.example.com",  # Missing @
            ""
        ]

        for email in invalid_emails:
            result = analyzer.validate_email(email)
            assert result is False

    def test_validate_phone_valid(self, analyzer):
        """Test phone number validation with valid data."""
        valid_phones = [
            "+79001234567",
            "89001234567",
            "+1(555)123-4567",
            "+44 20 7946 0958"
        ]

        for phone in valid_phones:
            result = analyzer.validate_phone(phone)
            assert result is True

    def test_validate_phone_invalid(self, analyzer):
        """Test phone number validation with invalid data."""
        invalid_phones = [
            "12345",  # Too short
            "abcdef",  # Contains letters
            "+1234567890123456",  # Too long
            ""
        ]

        for phone in invalid_phones:
            result = analyzer.validate_phone(phone)
            assert result is False

    def test_validate_ip_valid(self, analyzer):
        """Test IP address validation with valid data."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "8.8.8.8"
        ]

        for ip in valid_ips:
            result = analyzer.validate_ip(ip)
            assert result is True

    def test_validate_ip_invalid(self, analyzer):
        """Test IP address validation with invalid data."""
        invalid_ips = [
            "256.256.256.256",  # Octet > 255
            "192.168.1",  # Missing octet
            "192.168.1.1.1",  # Too many octets
            "192.168.1.abc",  # Contains letters
            ""
        ]

        for ip in invalid_ips:
            result = analyzer.validate_ip(ip)
            assert result is False

    def test_validate_domain_valid(self, analyzer):
        """Test domain validation with valid data."""
        valid_domains = [
            "example.com",
            "sub.example.co.uk",
            "test-site.org",
            "domain123.net"
        ]

        for domain in valid_domains:
            result = analyzer.validate_domain(domain)
            assert result is True

    def test_validate_domain_invalid(self, analyzer):
        """Test domain validation with invalid data."""
        invalid_domains = [
            ".example.com",  # Starts with dot
            "example..com",  # Double dot
            "example",  # No TLD
            "-example.com",  # Starts with hyphen
            ""
        ]

        for domain in invalid_domains:
            result = analyzer.validate_domain(domain)
            assert result is False

    @pytest.mark.asyncio
    async def test_search_email_breaches(self, analyzer):
        """Test searching for email breaches."""
        with patch('modules.network_analyzer.NetworkAnalyzer._check_haveibeenpwned',
                   new_callable=AsyncMock) as mock_check:
            mock_check.return_value = [
                {"name": "Breach1", "date": "2020-01-01"},
                {"name": "Breach2", "date": "2021-05-15"}
            ]

            result = await analyzer.search_email_breaches("user@example.com")

            assert len(result) == 2
            assert result[0]["name"] == "Breach1"
            assert result[1]["name"] == "Breach2"
            mock_check.assert_called_once_with("user@example.com")

        @pytest.mark.asyncio
        async def test_analyze_ip_geolocation(self, analyzer):
            """Test IP geolocation analysis."""
            with patch('modules.network_analyzer.NetworkAnalyzer._get_ip_geolocation',
                       new_callable=AsyncMock) as mock_geo:
                mock_geo.return_value = {
                    "ip": "8.8.8.8",
                    "country": "United States",
                    "city": "Mountain View",
                    "isp": "Google LLC"
                }

                result = await analyzer.analyze_ip_geolocation("8.8.8.8")

                assert result["ip"] == "8.8.8.8"
                assert result["country"] == "United States"
                assert result["city"] == "Mountain View"
                assert result["isp"] == "Google LLC"
                mock_geo.assert_called_once_with("8.8.8.8")

        @pytest.mark.asyncio
        async def test_analyze_domain_whois(self, analyzer):
            """Test domain WHOIS analysis."""
            with patch('modules.network_analyzer.NetworkAnalyzer._get_domain_whois',
                       new_callable=AsyncMock) as mock_whois:
                mock_whois.return_value = {
                    "domain": "example.com",
                    "registrar": "Example Registrar",
                    "creation_date": "2010-01-01",
                    "expiration_date": "2025-01-01"
                }

                result = await analyzer.analyze_domain_whois("example.com")

                assert result["domain"] == "example.com"
                assert result["registrar"] == "Example Registrar"
                assert result["creation_date"] == "2010-01-01"
                assert result["expiration_date"] == "2025-01-01"
                mock_whois.assert_called_once_with("example.com")

        @pytest.mark.asyncio
        async def test_phone_number_lookup(self, analyzer):
            """Test phone number lookup."""
            with patch('modules.network_analyzer.NetworkAnalyzer._lookup_phone', new_callable=AsyncMock) as mock_lookup:
                mock_lookup.return_value = {
                    "phone": "+79001234567",
                    "country": "Russia",
                    "operator": "MTS",
                    "region": "Moscow"
                }

                result = await analyzer.phone_number_lookup("+79001234567")

                assert result["phone"] == "+79001234567"
                assert result["country"] == "Russia"
                assert result["operator"] == "MTS"
                assert result["region"] == "Moscow"
                mock_lookup.assert_called_once_with("+79001234567")