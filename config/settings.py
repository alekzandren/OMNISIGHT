import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseSettings, Field, validator

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

for directory in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """
    Основные настройки конфигурации для OmniSight OSINT Framework
    """
    app_name: str = "OmniSight"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="OMNISIGHT_DEBUG")
    max_workers: int = Field(default=50, env="OMNISIGHT_MAX_WORKERS")
    request_timeout: int = Field(default=30, env="OMNISIGHT_REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="OMNISIGHT_MAX_RETRIES")

    use_proxy: bool = Field(default=True, env="OMNISIGHT_USE_PROXY")
    proxy_rotation_interval: int = Field(default=10, env="OMNISIGHT_PROXY_ROTATION")
    proxy_file: str = Field(default="config/proxies.txt")

    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]

    api_keys: Dict[str, str] = {
        "haveibeenpwned": Field(default="", env="HIBP_API_KEY"),
        "leakcheck": Field(default="", env="LEAKCHECK_API_KEY"),
        "socialscan": Field(default="", env="SOCIALSCAN_API_KEY"),
        "ipinfo": Field(default="", env="IPINFO_API_KEY"),
        "virustotal": Field(default="", env="VIRUSTOTAL_API_KEY"),
    }

    identity_regex: Dict[str, str] = {
        "passport_ru": r"\d{4} \d{6}",
        "snils": r"\d{3}-\d{3}-\d{3} \d{2}",
        "driver_license_ru": r"\d{2} \d{2} \d{6}",
        "passport_international": r"[A-Z]{1,2}\d{6,9}",
        "green_card": r"[A-Z]{3}\d{8,9}",
    }

    migration_apis: Dict[str, Dict[str, Any]] = {
        "karta_polaka": {
            "base_url": "https://api.gov.pl/karta-polaka",
            "endpoints": {
                "verify": "/verify",
                "status": "/status",
            },
            "required_fields": ["pesel", "name", "surname"],
        },
        "vnzh_pmzh": {
            "base_url": "https://api.migration.gov.ru",
            "endpoints": {
                "verify": "/verify",
                "status": "/status",
            },
            "required_fields": ["passport_number", "name", "surname"],
        },
        "green_card": {
            "base_url": "https://api.uscis.gov/green-card",
            "endpoints": {
                "verify": "/verify",
                "status": "/status",
            },
            "required_fields": ["case_number", "name", "surname"],
        },
    }

    social_platforms: Dict[str, Dict[str, Any]] = {
        "linkedin": {
            "base_url": "https://www.linkedin.com/in/",
            "search_endpoint": "https://www.linkedin.com/search/results/people/",
            "rate_limit": 100,
            "auth_required": True,
        },
        "instagram": {
            "base_url": "https://www.instagram.com/",
            "api_endpoint": "https://i.instagram.com/api/v1/users/web_profile_info/",
            "rate_limit": 200,
            "auth_required": False,
        },
        "x_twitter": {
            "base_url": "https://twitter.com/",
            "api_endpoint": "https://api.twitter.com/2/users/by/username/",
            "rate_limit": 300,
            "auth_required": True,
        },
    }

    network_apis: Dict[str, Dict[str, Any]] = {
        "haveibeenpwned": {
            "base_url": "https://haveibeenpwned.com/api/v3",
            "rate_limit": 1500,
            "endpoints": {
                "breachedaccount": "/breachedaccount/{account}",
                "breaches": "/breaches",
                "pasteaccount": "/pasteaccount/{account}",
            },
        },
        "hlr_lookup": {
            "base_url": "https://api.hlr-lookup.com/api/v1",
            "endpoints": {
                "lookup": "/lookup",
            },
        },
        "ipinfo": {
            "base_url": "https://ipinfo.io",
            "endpoints": {
                "ip": "/{ip}/json",
                "domain": "/{domain}/json",
            },
        },
    }

    darknet_config: Dict[str, Any] = {
        "tor": {
            "socks_port": 9050,
            "control_port": 9051,
            "password": "",
            "circuit_build_timeout": 60,
            "max_circuit_build_attempts": 3,
        },
        "i2p": {
            "socks_port": 4444,
            "sam_port": 7656,
        },
        "marketplaces": [
            "http://darkmarket123.onion",
            "http://leakmarket456.onion",
        ],
        "paste_sites": [
            "http://pastebinabc.onion",
            "http://privatepaste789.onion",
        ],
    }

    export_formats: List[str] = ["json", "csv", "pdf"]
    export_dir: str = str(REPORTS_DIR)
    pdf_template: str = "reports/templates/report_template.html"

    log_level: str = Field(default="INFO", env="OMNISIGHT_LOG_LEVEL")
    log_file: str = str(LOGS_DIR / "omnisight.log")
    log_max_size: int = 10485760
    log_backup_count: int = 5

    max_concurrent_requests: int = 100
    rate_limit_delay: float = 0.1
    session_timeout: int = 3600

    cache_enabled: bool = True
    cache_ttl: int = 86400
    cache_dir: str = str(DATA_DIR / "cache")

    recursive_search_enabled: bool = True
    max_recursion_depth: int = 3
    recursion_modules: List[str] = ["identity", "social", "network", "migration"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("api_keys", pre=True)
    def validate_api_keys(cls, v):
        """Проверяет наличие необходимых API ключей"""
        required_keys = ["haveibeenpwned"]
        missing_keys = [key for key in required_keys if not v.get(key)]
        if missing_keys:
            import warnings
            warnings.warn(f"Отсутствуют API ключи для: {', '.join(missing_keys)}")
        return v

    @validator("max_workers")
    def validate_max_workers(cls, v):
        """Проверяет максимальное количество воркеров"""
        if v <= 0:
            raise ValueError("max_workers должно быть положительным числом")
        if v > 200:
            import warnings
            warnings.warn("max_workers слишком большое значение, может вызвать проблемы с производительностью")
        return v

    def get_proxy_list(self) -> List[str]:
        """Загружает список прокси из файла"""
        if not self.use_proxy:
            return []

        proxy_file = BASE_DIR / self.proxy_file
        if not proxy_file.exists():
            return []

        with open(proxy_file, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        return proxies

    def get_user_agent(self) -> str:
        """Возвращает случайный User-Agent из списка"""
        import random
        return random.choice(self.user_agents)

    def get_api_key(self, service: str) -> str:
        """Получает API ключ для указанного сервиса"""
        return self.api_keys.get(service, "")

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Возвращает конфигурацию для указанного модуля"""
        configs = {
            "identity": {
                "regex_patterns": self.identity_regex,
            },
            "migration": {
                "apis": self.migration_apis,
            },
            "social": {
                "platforms": self.social_platforms,
            },
            "network": {
                "apis": self.network_apis,
            },
            "darknet": {
                "config": self.darknet_config,
            },
        }
        return configs.get(module_name, {})


settings = Settings()


def get_settings() -> Settings:
    """Возвращает экземпляр настроек"""
    return settings


def update_settings(**kwargs) -> None:
    """Обновляет настройки"""
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
        else:
            raise ValueError(f"Неизвестный параметр настройки: {key}")


def save_settings(file_path: str = None) -> None:
    """Сохраняет настройки в файл"""
    import json
    from pathlib import Path

    if file_path is None:
        file_path = BASE_DIR / "settings.json"

    settings_dict = settings.dict()

    if "api_keys" in settings_dict:
        api_keys = settings_dict["api_keys"].copy()
        for key in api_keys:
            if api_keys[key]:
                api_keys[key] = "***REDACTED***"
        settings_dict["api_keys"] = api_keys

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(settings_dict, f, indent=4, ensure_ascii=False)

def load_settings(file_path: str = None) -> None:
    """Загружает настройки из файла"""
    import json
    from pathlib import Path

    if file_path is None:
        file_path = BASE_DIR / "settings.json"

    settings_file = Path(file_path)
    if not settings_file.exists():
        return

    with open(settings_file, 'r', encoding='utf-8') as f:
        settings_dict = json.load(f)

    if "api_keys" in settings_dict:
        api_keys = settings_dict.pop("api_keys")
        for key, value in settings_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        for key, value in api_keys.items():
            if key in settings.api_keys and not settings.api_keys[key] and value != "***REDACTED***":
                settings.api_keys[key] = value
    else:
        for key, value in settings_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)