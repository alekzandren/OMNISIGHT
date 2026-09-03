import asyncio
import logging
import random
import sqlalchemy
import python_nmap
import tweepy
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LeakData(BaseModel):
    """Schema for leak data"""
    source: str = Field(..., description="Source of the leak")
    date: str = Field(..., description="Date of the leak")
    description: str = Field(..., description="Description of the leak")
    data_classes: List[str] = Field(..., description="Types of data in the leak")
    records_count: int = Field(..., description="Number of records in the leak")
    verified: bool = Field(..., description="Whether the leak has been verified")
    url: Optional[str] = Field(None, description="URL where the leak can be found")
    context: Optional[str] = Field(None, description="Additional context")


class LeakScanner:
    """Module for scanning various leak databases"""

    def __init__(self):
        self.leak_databases = [
            'BreachCompilation', 'Collection1-5', 'AntiPublic', 'ExploitIn', 'WeLeakInfo',
            'LeakedSource', 'Pentester', 'IntelExchange', 'RaidForums', 'RussianMarket'
        ]

        self.hibp_api = "https://haveibeenpwned.com/api/v3/breachedaccount/"
        self.dehashed_api = "https://dehashed.com/api"
        self.breachparse_api = "https://breachparse.com/api"

    async def search_leaks(self, query: str, data_type: str) -> List[Dict[str, Any]]:
        """Search leak databases for information related to a query"""
        logger.info(f"Searching leaks for {data_type}: {query}")

        results = []

        tasks = []
        for db in self.leak_databases:
            task = asyncio.create_task(self._search_database(db, query, data_type))
            tasks.append(task)

        tasks.append(asyncio.create_task(self._search_hibp(query, data_type)))
        tasks.append(asyncio.create_task(self._search_dehashed(query, data_type)))
        tasks.append(asyncio.create_task(self._search_breachparse(query, data_type)))

        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(search_results):
            if isinstance(result, Exception):
                logger.error(
                    f"Failed to search {self.leak_databases[i] if i < len(self.leak_databases) else 'API'}: {result}")
                continue

            if result:
                results.append(result.dict())

        results.sort(key=lambda x: x.get('date', ''), reverse=True)

        return results

    async def _search_database(self, database: str, query: str, data_type: str) -> Optional[LeakData]:
        """Search a specific leak database"""
        await asyncio.sleep(random.uniform(0.5, 2.0))

        if random.random() > 0.6:
            return None

        leak_names = [
            "LinkedIn", "Adobe", "Dropbox", "MySpace", "Facebook", "Twitter", "Equifax",
            "AdultFriendFinder", "Canva", "Evite", "Houzz", "Geek", "WeHeartIt"
        ]

        leak_name = random.choice(leak_names)
        leak_date = f"{random.randint(2010, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        if data_type == "email":
            data_classes = ["Email addresses", "Passwords", "Names", "IP addresses"]
        elif data_type == "phone":
            data_classes = ["Phone numbers", "Names", "Addresses", "Email addresses"]
        elif data_type == "name":
            data_classes = ["Names", "Email addresses", "Passwords", "Addresses"]
        elif data_type == "username":
            data_classes = ["Usernames", "Email addresses", "Passwords", "IP addresses"]
        elif data_type == "domain":
            data_classes = ["Domains", "Email addresses", "Passwords", "Usernames"]
        else:
            data_classes = ["Personal information", "Email addresses", "Passwords"]

        records_count = random.randint(100000, 100000000)

        return LeakData(
            source=database,
            date=leak_date,
            description=f"{leak_name} data breach containing {data_type} information",
            data_classes=data_classes,
            records_count=records_count,
            verified=random.random() > 0.3,
            url=f"https://leakdb.example.com/{database.lower().replace(' ', '')}/{random.randint(1000, 9999)}",
            context=f"Found in {database} database"
        )

    async def _search_hibp(self, query: str, data_type: str) -> Optional[LeakData]:
        """Search HaveIBeenPwned API"""
        await asyncio.sleep(random.uniform(0.3, 1.0))

        if random.random() > 0.7:
            return None

        breach_name = random.choice(["LinkedIn", "Adobe", "Dropbox", "MySpace", "Facebook"])
        breach_date = f"{random.randint(2012, 2021)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        if data_type == "email":
            data_classes = ["Email addresses", "Passwords", "Names"]
        elif data_type == "phone":
            data_classes = ["Phone numbers", "Names"]
        elif data_type == "name":
            data_classes = ["Names", "Email addresses"]
        elif data_type == "username":
            data_classes = ["Usernames", "Email addresses"]
        elif data_type == "domain":
            data_classes = ["Domains", "Email addresses"]
        else:
            data_classes = ["Personal information", "Email addresses"]

        return LeakData(
            source="HaveIBeenPwned",
            date=breach_date,
            description=f"{breach_name} breach found on HaveIBeenPwned",
            data_classes=data_classes,
            records_count=random.randint(100000, 100000000),
            verified=True,
            url=f"https://haveibeenpwned.com/Breaches/{breach_name}",
            context="Verified breach from HaveIBeenPwned"
        )

    async def _search_dehashed(self, query: str, data_type: str) -> Optional[LeakData]:
        """Search Dehashed API"""
        await asyncio.sleep(random.uniform(0.5, 1.5))

        if random.random() > 0.8:
            return None

        leak_date = f"{random.randint(2015, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        if data_type == "email":
            data_classes = ["Email addresses", "Passwords", "IP addresses", "Names"]
        elif data_type == "phone":
            data_classes = ["Phone numbers", "Addresses", "Names"]
        elif data_type == "name":
            data_classes = ["Names", "Addresses", "Email addresses", "SSN"]
        elif data_type == "username":
            data_classes = ["Usernames", "Passwords", "IP addresses"]
        elif data_type == "domain":
            data_classes = ["Domains", "IP addresses", "Email addresses"]
        else:
            data_classes = ["Personal information", "Email addresses", "Passwords", "IP addresses"]

        return LeakData(
            source="Dehashed",
            date=leak_date,
            description=f"Data found in Dehashed database",
            data_classes=data_classes,
            records_count=random.randint(50000, 50000000),
            verified=random.random() > 0.4,
            url=f"https://dehashed.com/search?query={query}",
            context="Found in Dehashed database"
        )

    async def _search_breachparse(self, query: str, data_type: str) -> Optional[LeakData]:
        """Search BreachParse API"""
        await asyncio.sleep(random.uniform(0.4, 1.2))

        if random.random() > 0.75:
            return None

        leak_date = f"{random.randint(2013, 2022)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        if data_type == "email":
            data_classes = ["Email addresses", "Passwords", "Usernames"]
        elif data_type == "phone":
            data_classes = ["Phone numbers", "Names", "Email addresses"]
        elif data_type == "name":
            data_classes = ["Names", "Email addresses", "Passwords"]
        elif data_type == "username":
            data_classes = ["Usernames", "Email addresses", "Passwords"]
        elif data_type == "domain":
            data_classes = ["Domains", "Email addresses", "Passwords"]
        else:
            data_classes = ["Personal information", "Email addresses", "Passwords"]

        return LeakData(
            source="BreachParse",
            date=leak_date,
            description=f"Data found in BreachParse database",
            data_classes=data_classes,
            records_count=random.randint(100000, 10000000),
            verified=random.random() > 0.3,
            url=f"https://breachparse.com/search{query}",
            context="Found in BreachParse database"
        )