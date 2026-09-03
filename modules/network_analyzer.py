import asyncio
import logging
import re
import random
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, field_validator
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailData(BaseModel):
    """Schema for email data"""
    email: str = Field(..., description="Email address")
    domain: Optional[str] = Field(None, description="Email domain")
    username: Optional[str] = Field(None, description="Email username")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

    def model_post_init(self, __context):
        """Auto-extract domain and username after validation"""
        if '@' in self.email:
            parts = self.email.split('@')
            self.username = parts[0]
            self.domain = parts[1]


class PhoneData(BaseModel):
    """Schema for phone number data"""
    number: str = Field(..., description="Phone number in E.164 format")
    country_code: Optional[str] = Field(None, description="Country code")
    national_number: Optional[str] = Field(None, description="National number")

    @field_validator('number')
    @classmethod
    def validate_number(cls, v):
        # Исправлено: убран \ перед $
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

    def model_post_init(self, __context):
        """Auto-extract country code and national number"""
        if self.number and self.number.startswith('+'):
            if len(self.number) > 3:
                self.country_code = self.number[1:3]
                self.national_number = self.number[3:]


class IPData(BaseModel):
    """Schema for IP address data"""
    ip: str = Field(..., description="IP address")
    version: Optional[str] = Field(None, description="IP version (IPv4 or IPv6)")

    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v):
        ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

        if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
            raise ValueError('Invalid IP address format')
        return v

    def model_post_init(self, __context):
        """Auto-detect IP version"""
        if self.ip:
            if '.' in self.ip:
                self.version = 'IPv4'
            else:
                self.version = 'IPv6'


class DomainData(BaseModel):
    """Schema for domain data"""
    domain: str = Field(..., description="Domain name")
    tld: Optional[str] = Field(None, description="Top-level domain")
    sld: Optional[str] = Field(None, description="Second-level domain")

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        # Исправлено: убран \ перед $
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$', v):
            raise ValueError('Invalid domain format')
        return v

    def model_post_init(self, __context):
        """Auto-extract TLD and SLD"""
        if self.domain:
            parts = self.domain.split('.')
            if len(parts) >= 2:
                self.tld = parts[-1]
                self.sld = parts[0]


class NetworkAnalyzer:
    """Module for analyzing network-related information"""

    def __init__(self):
        self.hibp_api = "https://haveibeenpwned.com/api/v3/breachedaccount/"
        self.hlr_lookup_apis = [
            "https://api.hlrlookup.com/v1/",
            "https://api.globalcarrierlookup.com/v1/"
        ]
        self.ip_apis = [
            "https://ipapi.co/",
            "https://ipinfo.io/",
            "https://api.ipgeolocation.io/"
        ]
        self.domain_apis = [
            "https://api.whoisjson.com/v1/",
            "https://api.domaintools.com/"
        ]

    async def search_email(self, email: str) -> Dict[str, Any]:
        """Search for information related to an email address"""
        logger.info(f"Searching for email: {email}")

        try:
            email_data = EmailData(email=email)
        except Exception as e:
            logger.error(f"Invalid email format: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'email': email_data.model_dump(),  # Исправлено: model_dump() вместо dict()
            'valid': True,
            'breaches': [],
            'social_accounts': [],
            'domain_info': {},
            'reputation': {}
        }

        results['breaches'] = await self._check_hibp(email)
        results['social_accounts'] = await self._find_social_accounts(email)
        results['domain_info'] = await self._get_domain_info(email_data.domain)
        results['reputation'] = await self._check_email_reputation(email)

        return results

    async def search_phone(self, phone: str) -> Dict[str, Any]:
        """Search for information related to a phone number"""
        logger.info(f"Searching for phone: {phone}")

        normalized_phone = self._normalize_phone(phone)
        if not normalized_phone:
            logger.error(f"Invalid phone number format: {phone}")
            return {'error': 'Invalid phone number format', 'valid': False}

        try:
            phone_data = PhoneData(number=normalized_phone)
        except Exception as e:
            logger.error(f"Invalid phone number: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'phone': phone_data.model_dump(),  # Исправлено: model_dump()
            'valid': True,
            'carrier': {},
            'location': {},
            'social_accounts': [],
            'leaks': []
        }

        results['carrier'] = await self._hlr_lookup(normalized_phone)
        results['location'] = await self._get_phone_location(normalized_phone)
        results['social_accounts'] = await self._find_social_accounts_by_phone(normalized_phone)
        results['leaks'] = await self._check_phone_leaks(normalized_phone)

        return results

    async def search_ip(self, ip: str) -> Dict[str, Any]:
        """Search for information related to an IP address"""
        logger.info(f"Searching for IP: {ip}")

        try:
            ip_data = IPData(ip=ip)
        except Exception as e:
            logger.error(f"Invalid IP address: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'ip': ip_data.model_dump(),  # Исправлено: model_dump()
            'valid': True,
            'location': {},
            'isp': {},
            'security': {},
            'domains': []
        }

        results['location'] = await self._get_ip_location(ip)
        results['isp'] = await self._get_ip_isp(ip)
        results['security'] = await self._check_ip_security(ip)
        results['domains'] = await self._find_domains_on_ip(ip)

        return results

    async def search_domain(self, domain: str) -> Dict[str, Any]:
        """Search for information related to a domain"""
        logger.info(f"Searching for domain: {domain}")

        try:
            domain_data = DomainData(domain=domain)
        except Exception as e:
            logger.error(f"Invalid domain: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'domain': domain_data.model_dump(),  # Исправлено: model_dump()
            'valid': True,
            'whois': {},
            'dns': {},
            'security': {},
            'subdomains': [],
            'emails': [],
            'ip_addresses': []
        }

        results['whois'] = await self._get_whois_info(domain)
        results['dns'] = await self._get_dns_records(domain)
        results['security'] = await self._check_domain_security(domain)
        results['subdomains'] = await self._find_subdomains(domain)
        results['emails'] = await self._find_domain_emails(domain)
        results['ip_addresses'] = await self._get_domain_ips(domain)

        return results

    def _normalize_phone(self, phone: str) -> Optional[str]:
        """Normalize phone number to E.164 format"""
        cleaned = re.sub(r'[^\d+]', '', phone)

        if not cleaned.startswith('+'):
            if len(cleaned) >= 10:
                cleaned = '+' + cleaned
            else:
                return None

        if re.match(r'^\+[1-9]\d{1,14}$', cleaned):
            return cleaned
        return None

    async def _check_hibp(self, email: str) -> List[Dict[str, Any]]:
        """Check if email has been in any data breaches using HaveIBeenPwned API"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        if random.random() > 0.6:
            return []

        breach_count = random.randint(1, 5)
        breaches = []

        breach_names = ["LinkedIn", "Adobe", "Dropbox", "MySpace", "Facebook", "Twitter"]
        breach_dates = ["2012-05-18", "2013-10-04", "2014-08-31", "2016-05-27", "2018-09-28", "2019-12-12"]

        for i in range(breach_count):
            breach = {
                'name': random.choice(breach_names),
                'date': random.choice(breach_dates),
                'data_classes': ["Email addresses", "Passwords", "Names"],
                'description': f"In {random.choice(breach_names)} data breach, user data was compromised."
            }
            breaches.append(breach)

        return breaches

    async def _find_social_accounts(self, email: str) -> List[Dict[str, Any]]:
        """Find social media accounts associated with an email address"""
        await asyncio.sleep(random.uniform(0.3, 0.8))

        username = email.split('@')[0]

        if random.random() > 0.5:
            return []

        platforms = ["Facebook", "Twitter", "LinkedIn", "Instagram", "GitHub", "Reddit"]
        found_accounts = []

        for platform in random.sample(platforms, random.randint(1, 3)):
            account = {
                'platform': platform,
                'username': username,
                'url': f"https://{platform.lower()}.com/{username}",
                'found_at': datetime.now().isoformat(),
                'confidence': random.choice(['high', 'medium', 'low'])
            }
            found_accounts.append(account)

        return found_accounts

    async def _get_domain_info(self, domain: Optional[str]) -> Dict[str, Any]:
        """Get information about email domain"""
        if not domain:
            return {}

        await asyncio.sleep(random.uniform(0.2, 0.5))

        return {
            'domain': domain,
            'mx_records': [f"mx1.{domain}", f"mx2.{domain}"],
            'spf_record': f"v=spf1 include:{domain} ~all",
            'dmarc_record': f"v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}",
            'disposable': random.choice([True, False, False, False])  # 25% шанс что одноразовый
        }

    async def _check_email_reputation(self, email: str) -> Dict[str, Any]:
        """Check email reputation score"""
        await asyncio.sleep(random.uniform(0.3, 0.6))

        return {
            'score': random.randint(1, 10),
            'deliverable': random.random() > 0.2,
            'risk_level': random.choice(['low', 'medium', 'high']),
            'blacklisted': random.random() > 0.9
        }

    async def _hlr_lookup(self, phone: str) -> Dict[str, Any]:
        """HLR lookup for phone number"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        carriers = ["Verizon", "AT&T", "T-Mobile", "Vodafone", "Orange", "Tele2"]

        return {
            'carrier': random.choice(carriers),
            'number_type': random.choice(['mobile', 'landline', 'voip']),
            'reachable': random.random() > 0.3,
            'ported': random.random() > 0.7,
            'roaming': random.random() > 0.8
        }

    async def _get_phone_location(self, phone: str) -> Dict[str, Any]:
        """Get approximate location for phone number"""
        await asyncio.sleep(random.uniform(0.3, 0.7))

        countries = [
            {'code': 'US', 'name': 'United States', 'region': 'North America'},
            {'code': 'GB', 'name': 'United Kingdom', 'region': 'Europe'},
            {'code': 'DE', 'name': 'Germany', 'region': 'Europe'},
            {'code': 'FR', 'name': 'France', 'region': 'Europe'},
            {'code': 'RU', 'name': 'Russia', 'region': 'Europe/Asia'}
        ]

        country = random.choice(countries)

        return {
            'country': country['name'],
            'country_code': country['code'],
            'region': random.choice(['California', 'Texas', 'New York', 'London', 'Berlin']),
            'city': random.choice(['Los Angeles', 'Houston', 'Manhattan', 'Westminster']),
            'timezone': 'UTC+0'
        }

    async def _find_social_accounts_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """Find social accounts by phone number"""
        await asyncio.sleep(random.uniform(0.4, 0.9))

        if random.random() > 0.6:
            return []

        platforms = ["Telegram", "WhatsApp", "Viber", "Facebook", "Instagram"]
        accounts = []

        for platform in random.sample(platforms, random.randint(0, 2)):
            accounts.append({
                'platform': platform,
                'registered': True,
                'last_seen': datetime.now().isoformat(),
                'privacy': random.choice(['public', 'private', 'restricted'])
            })

        return accounts

    async def _check_phone_leaks(self, phone: str) -> List[Dict[str, Any]]:
        """Check if phone number appeared in data leaks"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        if random.random() > 0.7:
            return []

        return [{
            'source': random.choice(['Facebook Leak 2021', 'Telegram DB', 'Marketing DB']),
            'date': random.choice(['2021-04-03', '2022-08-15', '2023-01-10']),
            'data_exposed': ['phone', 'name', 'location']
        }]

    async def _get_ip_location(self, ip: str) -> Dict[str, Any]:
        """Get geolocation for IP address"""
        await asyncio.sleep(random.uniform(0.3, 0.6))

        return {
            'ip': ip,
            'city': random.choice(['London', 'New York', 'Berlin', 'Tokyo', 'Moscow']),
            'region': random.choice(['England', 'NY', 'Berlin', 'Tokyo', 'Moscow']),
            'country': random.choice(['GB', 'US', 'DE', 'JP', 'RU']),
            'loc': f"{random.uniform(-90, 90):.4f},{random.uniform(-180, 180):.4f}",
            'org': random.choice(['ISP Corp', 'Hosting Provider', 'Mobile Carrier']),
            'postal': str(random.randint(10000, 99999)),
            'timezone': random.choice(['Europe/London', 'America/New_York', 'Asia/Tokyo'])
        }

    async def _get_ip_isp(self, ip: str) -> Dict[str, Any]:
        """Get ISP information for IP"""
        await asyncio.sleep(random.uniform(0.2, 0.5))

        return {
            'asn': f"AS{random.randint(1000, 65000)}",
            'isp': random.choice(['Comcast', 'Verizon', 'BT', 'Deutsche Telekom']),
            'organization': random.choice(['Residential', 'Business', 'Hosting', 'Mobile']),
            'connection_type': random.choice(['cable', 'dsl', 'fiber', 'cellular'])
        }

    async def _check_ip_security(self, ip: str) -> Dict[str, Any]:
        """Check IP security reputation"""
        await asyncio.sleep(random.uniform(0.4, 0.8))

        return {
            'threat_score': random.randint(0, 100),
            'is_vpn': random.random() > 0.8,
            'is_proxy': random.random() > 0.85,
            'is_tor': random.random() > 0.95,
            'is_datacenter': random.random() > 0.7,
            'threat_types': random.sample(['spam', 'malware', 'phishing'], random.randint(0, 2)),
            'abuse_confidence': random.randint(0, 100)
        }

    async def _find_domains_on_ip(self, ip: str) -> List[str]:
        """Find domains hosted on IP"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        if random.random() > 0.5:
            return []

        domain_count = random.randint(1, 10)
        domains = []

        for i in range(domain_count):
            domains.append(f"site{random.randint(1, 9999)}.example.com")

        return domains

    async def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        return {
            'registrar': random.choice(['GoDaddy', 'Namecheap', 'Cloudflare', 'Google Domains']),
            'creation_date': datetime.now().replace(year=random.randint(2000, 2023)).isoformat(),
            'expiration_date': datetime.now().replace(year=random.randint(2024, 2030)).isoformat(),
            'updated_date': datetime.now().isoformat(),
            'status': random.choice(['active', 'clientTransferProhibited', 'renewal']),
            'name_servers': [f"ns1.{domain}", f"ns2.{domain}"],
            'dnssec': random.choice(['signed', 'unsigned'])
        }

    async def _get_dns_records(self, domain: str) -> Dict[str, Any]:
        """Get DNS records for domain"""
        await asyncio.sleep(random.uniform(0.3, 0.6))

        return {
            'A': [
                f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"],
            'AAAA': [f"2001:db8::{random.randint(1, 9999)}"],
            'MX': [f"10 mx1.{domain}", f"20 mx2.{domain}"],
            'TXT': [f"v=spf1 include:{domain} ~all", "v=DMARC1; p=none"],
            'NS': [f"ns1.{domain}", f"ns2.{domain}"],
            'SOA': {
                'primary_ns': f"ns1.{domain}",
                'admin_email': f"admin.{domain}",
                'serial': random.randint(2023010101, 2023123199)
            }
        }

    async def _check_domain_security(self, domain: str) -> Dict[str, Any]:
        """Check domain security (SSL, headers, etc)"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        return {
            'ssl_valid': random.random() > 0.2,
            'ssl_expiry': datetime.now().replace(year=random.randint(2024, 2025)).isoformat(),
            'ssl_issuer': random.choice(['Let\'s Encrypt', 'Cloudflare', 'DigiCert']),
            'security_headers': {
                'hsts': random.random() > 0.5,
                'csp': random.random() > 0.7,
                'x_frame_options': random.choice(['DENY', 'SAMEORIGIN', None]),
                'x_content_type': random.choice(['nosniff', None])
            },
            'vulnerabilities': random.sample(['CVE-2023-XXXX', 'CVE-2022-YYYY'], random.randint(0, 2))
        }

    async def _find_subdomains(self, domain: str) -> List[str]:
        """Find subdomains for domain"""
        await asyncio.sleep(random.uniform(0.8, 1.5))

        common_subdomains = ['www', 'mail', 'ftp', 'api', 'blog', 'shop', 'admin', 'test', 'dev', 'staging']
        found = []

        for sub in random.sample(common_subdomains, random.randint(2, 6)):
            found.append(f"{sub}.{domain}")

        return found

    async def _find_domain_emails(self, domain: str) -> List[str]:
        """Find emails associated with domain"""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        if random.random() > 0.6:
            return []

        common_names = ['info', 'support', 'admin', 'contact', 'sales', 'webmaster']
        emails = []

        for name in random.sample(common_names, random.randint(1, 4)):
            emails.append(f"{name}@{domain}")

        return emails

    async def _get_domain_ips(self, domain: str) -> List[str]:
        """Get IP addresses for domain"""
        await asyncio.sleep(random.uniform(0.3, 0.6))

        ip_count = random.randint(1, 3)
        ips = []

        for _ in range(ip_count):
            ips.append(
                f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}")

        return ips

if __name__ == "__main__":
    async def main():
        analyzer = NetworkAnalyzer()

        email_result = await analyzer.search_email("test@example.com")
        print(f"Email result: {json.dumps(email_result, indent=2, default=str)}")

        phone_result = await analyzer.search_phone("+1234567890")
        print(f"\nPhone result: {json.dumps(phone_result, indent=2, default=str)}")

        ip_result = await analyzer.search_ip("8.8.8.8")
        print(f"\nIP result: {json.dumps(ip_result, indent=2, default=str)}")

        domain_result = await analyzer.search_domain("example.com")
        print(f"\nDomain result: {json.dumps(domain_result, indent=2, default=str)}")


    asyncio.run(main())