import asyncio
import logging
import random
import python-docx
import jinja2
import re
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DocumentData(BaseModel):
    """Schema for document data"""
    document_type: str = Field(..., description="Type of document")
    document_number: str = Field(..., description="Document number")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    date_of_birth: Optional[str] = Field(None, description="Date of birth")
    place_of_birth: Optional[str] = Field(None, description="Place of birth")
    issue_date: Optional[str] = Field(None, description="Issue date")
    expiry_date: Optional[str] = Field(None, description="Expiry date")
    issuing_authority: Optional[str] = Field(None, description="Issuing authority")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Additional document-specific info")


class DocumentAnalyzer:
    """Module for analyzing document images and extracting information"""

    def __init__(self):
        self.ocr_engines = [
            "Tesseract", "Google Cloud Vision", "Amazon Textract", "Azure OCR"
        ]

        self.document_types = [
            "passport", "id_card", "driver_license", "birth_certificate",
            "social_security_card", "residence_permit", "military_id", "student_id"
        ]

    async def analyze_document(self, image_path: str, document_type: str) -> Dict[str, Any]:
        """Analyze a document image and extract information"""
        logger.info(f"Analyzing document image: {image_path}, type: {document_type}")

        if document_type not in self.document_types:
            logger.error(f"Unsupported document type: {document_type}")
            return {'error': f"Unsupported document type: {document_type}", 'valid': False}

            ocr_text = await self._perform_ocr(image_path)

            if not ocr_text:
                logger.error("Failed to extract text from image")
                return {'error': "Failed to extract text from image", 'valid': False}

            try:
                document_data = await self._extract_document_info(ocr_text, document_type)
                return {
                    'valid': True,
                    'document': document_data.dict(),
                    'confidence': random.uniform(0.7, 0.95),
                    'extracted_text': ocr_text
                }
            except Exception as e:
                logger.error(f"Failed to extract document info: {e}")
                return {'error': str(e), 'valid': False}

        async def _perform_ocr(self, image_path: str) -> str:
            """Perform OCR on the document image"""
            await asyncio.sleep(random.uniform(1.0, 3.0))

            mock_texts = {
                "passport": """
                        PASSPORT
                        United States of America
                        P < USA<DOE<JOHN<ROBERT<<<<<<<<<<<<<<<<<<<<<<<<
                        1234567890USA7301011M2101015<<<<<<<<<<<<<<04
                        DOE
                        JOHN ROBERT
                        Date of Birth: 01 Jan 1973
                        Place of Birth: NEW YORK, USA
                        Issue Date: 01 Jan 2021
                        Expiry Date: 01 Jan 2031
                        Authority: Department of State
                        """,

                "id_card": """
                        CALIFORNIA DRIVER LICENSE
                        DL 123456789
                        CLASS C
                        DOE, JOHN ROBERT
                        123 MAIN ST
                        ANYTOWN, CA 90210
                        DOB: 01/01/1973
                        EXP: 01/01/2025
                        ISS: 01/01/2020
                        SEX: M
                        HGT: 5'10"
                        WGT: 175 lbs
                        EYES: BLU
                        HAIR: BRO
                        """,

                "driver_license": """
                        NEW YORK DRIVER LICENSE
                        LICENSE NO: D123456789
                        CLASS: D
                        DOE, JOHN ROBERT
                        456 PARK AVE
                        NEW YORK, NY 10001
                        DOB: 01/01/1973
                        EXP: 01/01/2025
                        ISS: 01/01/2020
                        SEX: M
                        HGT: 5'10"
                        WGT: 175 lbs
                        EYES: BLU
                        HAIR: BRO
                        ORGAN DONOR: YES
                        """,

                "birth_certificate": """
                        STATE OF CALIFORNIA
                        CERTIFICATE OF LIVE BIRTH
                        FILE NO: 123-45-67890

                        CHILD'S NAME:
                        FIRST: JOHN ROBERT
                        LAST: DOE

                        DATE OF BIRTH: JANUARY 01, 1973
                        PLACE OF BIRTH: LOS ANGELES, CALIFORNIA
                        SEX: MALE

                        MOTHER'S NAME:
                        FIRST: JANE
                        LAST: DOE
                        MAIDEN NAME: SMITH

                        FATHER'S NAME:
                        FIRST: ROBERT
                        LAST: DOE

                        DATE OF REGISTRATION: JANUARY 15, 1973
                        REGISTRAR: L. JOHNSON
                        """,

                "social_security_card": """
                        SOCIAL SECURITY ADMINISTRATION
                        FOR SOCIAL SECURITY PURPOSES - NOT FOR IDENTIFICATION

                        SOCIAL SECURITY NUMBER
                        123-45-6789

                        NAME
                        JOHN ROBERT DOE

                        VALID FOR WORK ONLY WITH DHS AUTHORIZATION
                        """
            }

            return mock_texts.get(document_type,
                                  f"Document text for {document_type}\nDocument Number: {random.randint(10000000, 99999999)}\nName: JOHN DOE\nDate of Birth: 01/01/1973")

        async def _extract_document_info(self, ocr_text: str, document_type: str) -> DocumentData:
            """Extract information from OCR text based on document type"""
            if document_type == "passport":
                return self._extract_passport_info(ocr_text)
            elif document_type == "id_card":
                return self._extract_id_card_info(ocr_text)
            elif document_type == "driver_license":
                return self._extract_driver_license_info(ocr_text)
            elif document_type == "birth_certificate":
                return self._extract_birth_certificate_info(ocr_text)
            elif document_type == "social_security_card":
                return self._extract_ss_card_info(ocr_text)
            else:
                return self._extract_generic_document_info(ocr_text, document_type)

        def _extract_passport_info(self, text: str) -> DocumentData:
            """Extract information from passport OCR text"""
            doc_number_match = re.search(r'(\d{9})', text)
            doc_number = doc_number_match.group(1) if doc_number_match else "UNKNOWN"

            name_match = re.search(r'DOE\n(.*?)\n', text)
            name = name_match.group(1).strip() if name_match else "UNKNOWN"

            name_parts = name.split()
            first_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[
                0] if name_parts else "UNKNOWN"
            last_name = name_parts[-1] if name_parts else "UNKNOWN"

            dob_match = re.search(r'Date of Birth: (.*?)\n', text)
            dob = dob_match.group(1).strip() if dob_match else None

            pob_match = re.search(r'Place of Birth: (.*?)\n', text)
            pob = pob_match.group(1).strip() if pob_match else None

            issue_match = re.search(r'Issue Date: (.*?)\n', text)
            issue_date = issue_match.group(1).strip() if issue_match else None

            expiry_match = re.search(r'Expiry Date: (.*?)\n', text)
            expiry_date = expiry_match.group(1).strip() if expiry_match else None

            authority_match = re.search(r'Authority: (.*?)', text)
            authority = authority_match.group(1).strip() if authority_match else None

            return DocumentData(
                document_type="passport",
                document_number=doc_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                place_of_birth=pob,
                issue_date=issue_date,
                expiry_date=expiry_date,
                issuing_authority=authority,
                additional_info={"country": "United States"}
            )

        def _extract_id_card_info(self, text: str) -> DocumentData:
            """Extract information from ID card OCR text"""
            doc_number_match = re.search(r'DL (\d+)', text)
            doc_number = doc_number_match.group(1) if doc_number_match else "UNKNOWN"

            name_match = re.search(r'(.*?)\n\d+ .* ST', text)
            name = name_match.group(1).strip() if name_match else "UNKNOWN"

            name_parts = name.split(', ')
            last_name = name_parts[0] if len(name_parts) > 1 else name_parts[0] if name_parts else "UNKNOWN"
            first_name = name_parts[1] if len(name_parts) > 1 else "UNKNOWN"

            dob_match = re.search(r'DOB: (.*?)\n', text)
            dob = dob_match.group(1).strip() if dob_match else None

            expiry_match = re.search(r'EXP: (.*?)\n', text)
            expiry_date = expiry_match.group(1).strip() if expiry_match else None

            issue_match = re.search(r'ISS: (.*?)\n', text)
            issue_date = issue_match.group(1).strip() if issue_match else None

            sex_match = re.search(r'SEX: (.*?)\n', text)
            sex = sex_match.group(1).strip() if sex_match else None

            height_match = re.search(r'HGT: (.*?)\n', text)
            height = height_match.group(1).strip() if height_match else None

            weight_match = re.search(r'WGT: (.*?)\n', text)
            weight = weight_match.group(1).strip() if weight_match else None

            eyes_match = re.search(r'EYES: (.*?)\n', text)
            eyes = eyes_match.group(1).strip() if eyes_match else None

            hair_match = re.search(r'HAIR: (.*?)\n', text)
            hair = hair_match.group(1).strip() if hair_match else None

            return DocumentData(
                document_type="id_card",
                document_number=doc_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                issue_date=issue_date,
                expiry_date=expiry_date,
                issuing_authority="California DMV",
                additional_info={
                    "sex": sex,
                    "height": height,
                    "weight": weight,
                    "eye_color": eyes,
                    "hair_color": hair
                }
            )

        def _extract_driver_license_info(self, text: str) -> DocumentData:
            """Extract information from driver license OCR text"""
            # Extract document number
            doc_number_match = re.search(r'LICENSE NO: (.*?)\n', text)
            doc_number = doc_number_match.group(1).strip() if doc_number_match else "UNKNOWN"

            name_match = re.search(r'(.*?)\n\d+ .* AVE', text)
            name = name_match.group(1).strip() if name_match else "UNKNOWN"

            name_parts = name.split(', ')
            last_name = name_parts[0] if len(name_parts) > 1 else name_parts[0] if name_parts else "UNKNOWN"
            first_name = name_parts[1] if len(name_parts) > 1 else "UNKNOWN"

            dob_match = re.search(r'DOB: (.*?)\n', text)
            dob = dob_match.group(1).strip() if dob_match else None

            expiry_match = re.search(r'EXP: (.*?)\n', text)
            expiry_date = expiry_match.group(1).strip() if expiry_match else None

            issue_match = re.search(r'ISS: (.*?)\n', text)
            issue_date = issue_match.group(1).strip() if issue_match else None

            sex_match = re.search(r'SEX: (.*?)\n', text)
            sex = sex_match.group(1).strip() if sex_match else None

            height_match = re.search(r'HGT: (.*?)\n', text)
            height = height_match.group(1).strip() if height_match else None

            weight_match = re.search(r'WGT: (.*?)\n', text)
            weight = weight_match.group(1).strip() if weight_match else None

            eyes_match = re.search(r'EYES: (.*?)\n', text)
            eyes = eyes_match.group(1).strip() if eyes_match else None

            hair_match = re.search(r'HAIR: (.*?)\n', text)
            hair = hair_match.group(1).strip() if hair_match else None

            organ_match = re.search(r'ORGAN DONOR: (.*?)', text)
            organ_donor = organ_match.group(1).strip() if organ_match else None

            return DocumentData(
                document_type="driver_license",
                document_number=doc_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                issue_date=issue_date,
                expiry_date=expiry_date,
                issuing_authority="New York DMV",
                additional_info={
                    "sex": sex,
                    "height": height,
                    "weight": weight,
                    "eye_color": eyes,
                    "hair_color": hair,
                    "organ_donor": organ_donor
                }
            )

        def _extract_birth_certificate_info(self, text: str) -> DocumentData:
            """Extract information from birth certificate OCR text"""
            doc_number_match = re.search(r'FILE NO: (.*?)\n', text)
            doc_number = doc_number_match.group(1).strip() if doc_number_match else "UNKNOWN"

            first_name_match = re.search(r'FIRST: (.*?)\n', text)
            first_name = first_name_match.group(1).strip() if first_name_match else None

            last_name_match = re.search(r'LAST: (.*?)\n', text)
            last_name = last_name_match.group(1).strip() if last_name_match else None

            dob_match = re.search(r'DATE OF BIRTH: (.*?)\n', text)
            dob = dob_match.group(1).strip() if dob_match else None

            pob_match = re.search(r'PLACE OF BIRTH: (.*?)\n', text)
            pob = pob_match.group(1).strip() if pob_match else None

            sex_match = re.search(r'SEX: (.*?)\n', text)
            sex = sex_match.group(1).strip() if sex_match else None

            mother_match = re.search(r"MOTHER'S NAME:\nFIRST: (.*?)\nLAST: (.*?)\n", text)
            mother_first = mother_match.group(1).strip() if mother_match else None
            mother_last = mother_match.group(2).strip() if mother_match else None

            father_match = re.search(r"FATHER'S NAME:\nFIRST: (.*?)\nLAST: (.*?)\n", text)
            father_first = father_match.group(1).strip() if father_match else None
            father_last = father_match.group(2).strip() if father_match else None

            reg_match = re.search(r'DATE OF REGISTRATION: (.*?)\n', text)
            reg_date = reg_match.group(1).strip() if reg_match else None

            registrar_match = re.search(r'REGISTRAR: (.*?)', text)
            registrar = registrar_match.group(1).strip() if registrar_match else None

            return DocumentData(
                document_type="birth_certificate",
                document_number=doc_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                place_of_birth=pob,
                issue_date=reg_date,
                issuing_authority=registrar,
                additional_info={
                    "sex": sex,
                    "mother_first_name": mother_first,
                    "mother_last_name": mother_last,
                    "father_first_name": father_first,
                    "father_last_name": father_last
                }
            )

        def _extract_ss_card_info(self, text: str) -> DocumentData:
            """Extract information from Social Security card OCR text"""
            ssn_match = re.search(r'(\d{3}-\d{2}-\d{4})', text)
            doc_number = ssn_match.group(1) if ssn_match else "UNKNOWN"

            name_match = re.search(r'NAME\n(.*?)\n', text)
            name = name_match.group(1).strip() if name_match else "UNKNOWN"

            name_parts = name.split()
            first_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[
                0] if name_parts else "UNKNOWN"
            last_name = name_parts[-1] if name_parts else "UNKNOWN"

            auth_match = re.search(r'VALID FOR WORK (.*?)', text)
            auth = auth_match.group(1).strip() if auth_match else None

            return DocumentData(
                document_type="social_security_card",
                document_number=doc_number,
                first_name=first_name,
                last_name=last_name,
                issuing_authority="Social Security Administration",
                additional_info={
                    "work_authorization": auth
                }
            )

        def _extract_generic_document_info(self, text: str, document_type: str) -> DocumentData:
            """Extract information from generic document OCR text"""
            doc_number_match = re.search(r'(?:Number|No|ID):?\s*(\w+)', text, re.IGNORECASE)
            doc_number = doc_number_match.group(1).strip() if doc_number_match else "UNKNOWN"

            name_match = re.search(r'Name:?\s*([A-Z\s]+)', text, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else "UNKNOWN"

            name_parts = name.split()
            first_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[
                0] if name_parts else "UNKNOWN"
            last_name = name_parts[-1] if name_parts else "UNKNOWN"

            dob_match = re.search(r'(?:DOB|Date of Birth|Birth Date):?\s*([A-Za-z0-9\s/]+)', text, re.IGNORECASE)
            dob = dob_match.group(1).strip() if dob_match else None

            issue_match = re.search(r'(?:Issue Date|Issued|Date Issued):?\s*([A-Za-z0-9\s/]+)', text, re.IGNORECASE)
            issue_date = issue_match.group(1).strip() if issue_match else None

            expiry_match = re.search(r'(?:EXP|Expiry|Expires|Expiry Date):?\s*([A-Za-z0-9\s/]+)', text, re.IGNORECASE)
            expiry_date = expiry_match.group(1).strip() if expiry_match else None

            authority_match = re.search(r'(?:Authority|Issued by|Issuer):?\s*([A-Za-z0-9\s\.]+)', text, re.IGNORECASE)
            authority = authority_match.group(1).strip() if authority_match else None

            return DocumentData(
                document_type=document_type,
                document_number=doc_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                issue_date=issue_date,
                expiry_date=expiry_date,
                issuing_authority=authority,
                additional_info={}
            )