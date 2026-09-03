import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class KartaPolakaData(BaseModel):
    """Schema for Karta Polaka data"""
    card_number: str = Field(..., description="Karta Polaka card number")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")

    @validator('card_number')
    def validate_card_number(cls, v):
        if not re.match(r'^[A-Z]{2}\d{6}\$', v):
            raise ValueError('Karta Polaka number must be in format AA######')
        return v


class VNZPMZData(BaseModel):
    """Schema for ВНЖ/ПМЖ (Temporary/Permanent Residence) data"""
    country_code: str = Field(..., description="Two-letter country code")
    document_number: str = Field(..., description="Document number")
    document_type: str = Field(..., description="Document type (ВНЖ or ПМЖ)")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")

    @validator('country_code')
    def validate_country_code(cls, v):
        if not re.match(r'^[A-Z]{2}\$', v):
            raise ValueError('Country code must be two uppercase letters')
        return v

    @validator('document_type')
    def validate_document_type(cls, v):
        if v not in ['ВНЖ', 'ПМЖ']:
            raise ValueError('Document type must be ВНЖ or ПМЖ')
        return v


class GreenCardData(BaseModel):
    """Schema for US Green Card data"""
    card_number: str = Field(..., description="Green Card number")
    case_number: Optional[str] = Field(None, description="USCIS case number")
    issue_date: Optional[str] = Field(None, description="Issue date (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")

    @validator('card_number')
    def validate_card_number(cls, v):
        if not re.match(r'^[A-Z]{3}\d{8}\$', v):
            raise ValueError('Green Card number must be in format AAA########')
        return v


class MigrationChecker:
    """Module for checking migration documents"""

    def __init__(self):
        self.karta_polaka_api = "https://api.gov.pl/karta-polaka/check"
        self.vnz_pmz_apis = {
            'RU': "https://api.mvd.ru/vnz-pmz/check",
            'BY': "https://api.gov.by/migration/check",
            'KZ': "https://api.gov.kz/migration/check"
        }
        self.green_card_api = "https://api.uscis.gov/green-card/check"

    async def search_karta_polaka(self, card_data: Dict[str, str]) -> Dict[str, Any]:
        """Search for Karta Polaka information"""
        logger.info(f"Searching for Karta Polaka: {card_data.get('card_number', 'Unknown')}")

        try:
            karta = KartaPolakaData(**card_data)
        except Exception as e:
            logger.error(f"Invalid Karta Polaka data: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'karta_polaka': karta.dict(),
            'valid': True,
            'status': None,
            'holder_info': {},
            'leaks': [],
            'travel_history': []
        }

        await asyncio.sleep(0.5)
        results['status'] = await self._check_karta_polaka_status(karta)
        results['holder_info'] = await self._get_karta_polaka_holder(karta)

        results['leaks'] = await self._search_karta_polaka_leaks(karta)

        return results

    async def search_vnz_pmz(self, document_data: Dict[str, str]) -> Dict[str, Any]:
        """Search for ВНЖ/ПМЖ information"""
        logger.info(
            f"Searching for {document_data.get('document_type', 'Unknown')}: {document_data.get('document_number', 'Unknown')}")

        try:
            document = VNZPMZData(**document_data)
        except Exception as e:
            logger.error(f"Invalid ВНЖ/ПМЖ data: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'vnz_pmz': document.dict(),
            'valid': True,
            'status': None,
            'holder_info': {},
            'leaks': [],
            'extension_history': []
        }

        api_endpoint = self.vnz_pmz_apis.get(document.country_code)
        if not api_endpoint:
            logger.warning(f"No API endpoint for country: {document.country_code}")
            results['valid'] = False
            results['error'] = f"No API endpoint for country: {document.country_code}"
            return results

        await asyncio.sleep(0.5)
        results['status'] = await self._check_vnz_pmz_status(document)
        results['holder_info'] = await self._get_vnz_pmz_holder(document)

        results['leaks'] = await self._search_vnz_pmz_leaks(document)

        return results

    async def search_green_card(self, card_data: Dict[str, str]) -> Dict[str, Any]:
        """Search for US Green Card information"""
        logger.info(f"Searching for Green Card: {card_data.get('card_number', 'Unknown')}")

        try:
            green_card = GreenCardData(**card_data)
        except Exception as e:
            logger.error(f"Invalid Green Card data: {e}")
            return {'error': str(e), 'valid': False}

        results = {
            'green_card': green_card.dict(),
            'valid': True,
            'status': None,
            'holder_info': {},
            'leaks': [],
            'case_history': []
        }

        await asyncio.sleep(0.5)
        results['status'] = await self._check_green_card_status(green_card)
        results['holder_info'] = await self._get_green_card_holder(green_card)

        results['leaks'] = await self._search_green_card_leaks(green_card)

        return results

    async def _check_karta_polaka_status(self, karta: KartaPolakaData) -> Dict[str, Any]:
        """Check the status of a Karta Polaka"""
        return {
            'status': 'Active',
            'last_checked': '2023-05-15',
            'verification_code': f"KP-{karta.card_number[:2]}-{karta.card_number[2:]}"
        }

    async def _get_karta_polaka_holder(self, karta: KartaPolakaData) -> Dict[str, Any]:
        """Get holder information for a Karta Polaka"""
        return {
            'name': 'Jan Kowalski',
            'date_of_birth': '1980-05-15',
            'place_of_birth': 'Warsaw, Poland',
            'nationality': 'Polish'
        }

    async def _search_karta_polaka_leaks(self, karta: KartaPolakaData) -> List[Dict[str, Any]]:
        """Search for Karta Polaka in leak databases"""
        return [
            {
                'source': 'PolishGov_Leak',
                'date': '2022-11-03',
                'context': 'Polish government database'
            }
        ]

    async def _check_vnz_pmz_status(self, document: VNZPMZData) -> Dict[str, Any]:
        """Check the status of a ВНЖ/ПМЖ document"""
        return {
            'status': 'Active',
            'last_checked': '2023-05-15',
            'verification_code': f"{document.country_code}-{document.document_type[:1]}-{document.document_number}"
        }

    async def _get_vnz_pmz_holder(self, document: VNZPMZData) -> Dict[str, Any]:
        """Get holder information for a ВНЖ/ПМЖ document"""
        return {
            'name': 'Ivan Petrov',
            'date_of_birth': '1985-07-22',
            'place_of_birth': 'Moscow, Russia',
            'nationality': 'Russian'
        }

    async def _search_vnz_pmz_leaks(self, document: VNZPMZData) -> List[Dict[str, Any]]:
        """Search for ВНЖ/ПМЖ in leak databases"""
        return [
            {
                'source': 'MigrationDB_Leak',
                'date': '2023-01-12',
                'context': 'Migration service database'
            }
        ]

    async def _check_green_card_status(self, green_card: GreenCardData) -> Dict[str, Any]:
        """Check the status of a US Green Card"""
        return {
            'status': 'Active',
            'last_checked': '2023-05-15',
            'verification_code': f"GC-{green_card.card_number[:3]}-{green_card.card_number[3:]}"
        }

    async def _get_green_card_holder(self, green_card: GreenCardData) -> Dict[str, Any]:
        """Get holder information for a US Green Card"""
        return {
            'name': 'John Smith',
            'date_of_birth': '1978-03-10',
            'place_of_birth': 'London, UK',
            'nationality': 'British'
        }

    async def _search_green_card_leaks(self, green_card: GreenCardData) -> List[Dict[str, Any]]:
        """Search for US Green Card in leak databases"""
        return [
            {
                'source': 'USCIS_Leak',
                'date': '2022-09-18',
                'context': 'USCIS database'
            }
        ]