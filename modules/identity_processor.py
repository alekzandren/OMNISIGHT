import re
import asyncio
import logging
import matplotlib
import PyPDF2
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator, Field

logger = logging.getLogger(__name__)


class PassportData(BaseModel):
    """Schema for passport data"""
    country_code: str = Field(..., description="Two-letter country code")
    passport_number: str = Field(..., description="Passport number")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")
    full_name: Optional[str] = Field(None, description="Full name as in passport")

    @validator('country_code')
    def validate_country_code(cls, v):
        if not re.match(r'^[A-Z]{2}\$', v):
            raise ValueError('Country code must be two uppercase letters')
        return v

    @validator('passport_number')
    def validate_passport_number(cls, v):
        if len(v) < 6 or len(v) > 15:
            raise ValueError('Passport number must be between 6 and 15 characters')
        return v


class SNILSData(BaseModel):
    """Schema for Russian SNILS data"""
    number: str = Field(..., description="SNILS number in XXX-XXX-XXX-XX format")

    @validator('number')
    def validate_snils(cls, v):
        digits = re.sub(r'\D', '', v)

        if len(digits) != 11:
            raise ValueError('SNILS must contain 11 digits')

        formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:]}"
        return formatted


class DriversLicenseData(BaseModel):
    """Schema for driver's license data"""
    country_code: str = Field(..., description="Two-letter country code")
    license_number: str = Field(..., description="License number")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")
    full_name: Optional[str] = Field(None, description="Full name as in license")

    @validator('country_code')
    def validate_country_code(cls, v):
        if not re.match(r'^[A-Z]{2}\$', v):
            raise ValueError('Country code must be two uppercase letters')
        return v


class IdentityProcessor:
    """Module for processing identity documents"""

    def __init__(self):
        self.name_patterns = [
            r'^[A-Z][a-z]+ [A-Z][a-z]+\$',
            r'^[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\$',
            r'^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\$',
            r'^[А-Я][а-я]+ [А-Я][а-я]+\$',
            r'^[А-Я][а-я]+ [А-Я][а-я]+ [А-Я][а-я]+\$',
        ]

        self.passport_patterns = {
            'US': r'^[A-Z0-9]{9}\$',
            'RU': r'^[0-9]{2}[0-9]{2}[0-9]{6}\$',
            'EU': r'^[A-Z]{2}[0-9]{7}\$',
            'default': r'^[A-Z0-9]{6,15}\$'
        }

        self.driver_license_patterns = {
            'US': r'^[A-Z0-9]{1,12}\$',
            'RU': r'^[0-9]{2}[0-9]{2}[0-9]{6}\$',
            'EU': r'^[A-Z0-9]{1,15}\$',
            'default': r'^[A-Z0-9]{5,20}\$'
        }

    async def search_name(self, name: str) -> Dict[str, Any]:
        """Search for information based on a full name"""
        logger.info(f"Searching for name: {name}")
        results = {
            'name': name,
            'valid': self._validate_name(name),
            'potential_matches': [],
            'passport_hits': [],
            'license_hits': [],
            'snils_hits': []
        }

        if not results['valid']:
            logger.warning(f"Invalid name format: {name}")
            return results

        await asyncio.sleep(0.5)

        results['potential_matches'] = await self._generate_name_variants(name)

        return results

    async def process_passport(self, passport_data: Dict[str, str]) -> Dict[str, Any]:
        """Process passport data and search for related information"""
        logger.info(f"Processing passport data for country: {passport_data.get('country_code', 'Unknown')}")

        try:
            passport = PassportData(**passport_data)
        except Exception as e:
            logger.error(f"Invalid passport data: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'passport': passport.dict(),
            'valid': True,
            'leaks': [],
            'travel_records': [],
            'associated_documents': []
        }

        country_code = passport.country_code
        pattern = self.passport_patterns.get(country_code, self.passport_patterns['default'])

        if not re.match(pattern, passport.passport_number):
            logger.warning(f"Passport number doesn't match expected format for {country_code}")
            results['valid'] = False
            results['error'] = f"Passport number doesn't match expected format for {country_code}"
            return results

        await asyncio.sleep(0.5)
        results['leaks'] = await self._search_passport_leaks(passport)

        return results

    async def process_snils(self, snils_number: str) -> Dict[str, Any]:
        """Process Russian SNILS number and search for related information"""
        logger.info(f"Processing SNILS: {snils_number[:3]}-***-***-{snils_number[-2:]}")

        try:
            snils = SNILSData(number=snils_number)
        except Exception as e:
            logger.error(f"Invalid SNILS data: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'snils': snils.dict(),
            'valid': True,
            'leaks': [],
            'pension_records': [],
            'employment_history': []
        }

        digits = re.sub(r'\D', '', snils.number)
        if not self._validate_snils_checksum(digits):
            logger.warning("Invalid SNILS checksum")
            results['valid'] = False
            results['error'] = "Invalid SNILS checksum"
            return results

        await asyncio.sleep(0.5)
        results['leaks'] = await self._search_snils_leaks(snils)

        return results

    async def process_drivers_license(self, license_data: Dict[str, str]) -> Dict[str, Any]:
        """Process driver's license data and search for related information"""
        logger.info(f"Processing driver's license for country: {license_data.get('country_code', 'Unknown')}")

        try:
            license_obj = DriversLicenseData(**license_data)
        except Exception as e:
            logger.error(f"Invalid driver's license data: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'license': license_obj.dict(),
            'valid': True,
            'violations': [],
            'vehicle_records': [],
            'associated_documents': []
        }

        country_code = license_obj.country_code
        pattern = self.driver_license_patterns.get(country_code, self.driver_license_patterns['default'])

        if not re.match(pattern, license_obj.license_number):
            logger.warning(f"License number doesn't match expected format for {country_code}")
            results['valid'] = False
            results['error'] = f"License number doesn't match expected format for {country_code}"
            return results

        await asyncio.sleep(0.5)
        results['violations'] = await self._search_license_violations(license_obj)

        return results

    def _validate_name(self, name: str) -> bool:
        """Validate if the name matches any of the known patterns"""
        for pattern in self.name_patterns:
            if re.match(pattern, name):
                return True
        return False

    async def _generate_name_variants(self, name: str) -> List[str]:
        """Generate potential name variants for broader search"""
        parts = name.split()
        variants = []

        if len(parts) == 2:
            first, last = parts
            variants.append(f"{first} {last[0]}.")
            variants.append(f"{last}, {first}")
            variants.append(f"{first} M. {last}")
        elif len(parts) == 3:
            if '.' in parts[1]:
                first, middle_initial, last = parts
                variants.append(f"{first} M. {last}")
                variants.append(f"{first} {last}")
            else:
                first, middle, last = parts
                variants.append(f"{first} {middle[0]}. {last}")
                variants.append(f"{first} {last}")

        return variants

    def _validate_snils_checksum(self, digits: str) -> bool:
        """Validate SNILS checksum using the official algorithm"""
        if len(digits) != 11:
            return False

        check_sum = 0
        for i in range(9):
            check_sum += int(digits[i]) * (9 - i)

        check_sum = check_sum % 101
        if check_sum == 100:
            check_sum = 0
        elif check_sum == 101:
            check_sum = 0

        return check_sum == int(digits[9:11])

    async def _search_passport_leaks(self, passport: PassportData) -> List[Dict[str, Any]]:
        """Simulate searching for passport in leak databases"""
        return [
            {
                'source': 'LeakDB_A',
                'date': '2023-05-12',
                'context': 'Travel booking database'
            },
            {
                'source': 'LeakDB_B',
                'date': '2022-11-03',
                'context': 'Immigration records'
            }
        ]

    async def _search_snils_leaks(self, snils: SNILSData) -> List[Dict[str, Any]]:
        """Simulate searching for SNILS in leak databases"""
        return [
            {
                'source': 'PensionDB_Leak',
                'date': '2023-02-15',
                'context': 'Pension fund records'
            },
            {
                'source': 'EmploymentDB_Leak',
                'date': '2022-08-21',
                'context': 'Employment history database'
            }
        ]

    async def _search_license_violations(self, license_obj: DriversLicenseData) -> List[Dict[str, Any]]:
        """Simulate searching for license violations in traffic databases"""
        return [
            {
                'date': '2023-04-10',
                'violation': 'Speeding',
                'location': 'Moscow, Leninsky Prospekt'
            },
            {
                'date': '2022-12-05',
                'violation': 'Parking violation',
                'location': 'St. Petersburg, Nevsky Prospekt'
            }
        ]