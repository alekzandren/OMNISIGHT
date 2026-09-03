import re
import random
import string
from typing import Dict, List, Any, Optional
import hashlib
import base64
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    # International format
    pattern1 = r'\+\d{1,3}\s?\d{1,14}(\s?\d{1,13})?'
    # US format
    pattern2 = r'$$?\d{3}$$?[-.\s]?\d{3}[-.\s]?\d{4}'

    phones = re.findall(pattern1, text)
    phones.extend(re.findall(pattern2, text))

    # Clean up the results
    cleaned_phones = []
    for phone in phones:
        if isinstance(phone, tuple):
            phone = ''.join(phone)
        cleaned_phones.append(re.sub(r'[^\d+]', '', phone))

    return cleaned_phones


def extract_names(text: str) -> List[str]:
    """Extract potential names from text"""
    # This is a simplified approach - in a real implementation, you'd use NLP
    # Look for capitalized words that could be names
    words = text.split()
    potential_names = []

    for i in range(len(words) - 1):
        # Look for two consecutive capitalized words
        if (words[i].istitle() and words[i + 1].istitle() and
                len(words[i]) > 1 and len(words[i + 1]) > 1 and
                not words[i].endswith('.') and not words[i + 1].endswith('.')):
            potential_names.append(f"{words[i]} {words[i + 1]}")

    return potential_names


def extract_usernames(text: str) -> List[str]:
    """Extract potential usernames from text"""
    # Common username patterns
    pattern = r'\b[A-Za-z0-9_]{3,20}\b'
    all_matches = re.findall(pattern, text)

    # Filter out common words
    common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our',
                    'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way',
                    'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']

    usernames = []
    for match in all_matches:
        if match.lower() not in common_words:
            usernames.append(match)

    return usernames


def extract_domains(text: str) -> List[str]:
    """Extract domain names from text"""
    pattern = r'\b(?:https?://)?(?:www\.)?([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
    matches = re.findall(pattern, text)

    # Clean up the results
    domains = []
    for match in matches:
        # Remove paths and query parameters
        domain = match.split('/')[0]
        domains.append(domain)

    return domains


def extract_ip_addresses(text: str) -> List[str]:
    """Extract IP addresses from text"""
    # IPv4 pattern
    ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

    # IPv6 pattern (simplified)
    ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'

    ips = re.findall(ipv4_pattern, text)
    ips.extend(re.findall(ipv6_pattern, text))

    return ips


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_id() -> str:
    """Generate a random ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = generate_random_string(6)
    return f"{timestamp}_{random_str}"


def hash_string(text: str, salt: str = "") -> str:
    """Hash a string with optional salt"""
    if salt:
        text = f"{text}{salt}"
    return hashlib.sha256(text.encode()).hexdigest()


def encode_base64(text: str) -> str:
    """Encode text to base64"""
    return base64.b64encode(text.encode()).decode()


def decode_base64(encoded_text: str) -> str:
    """Decode base64 to text"""
    return base64.b64decode(encoded_text.encode()).decode()


def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """Save data to a JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {filepath}: {e}")
        return False


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from a JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {filepath}: {e}")
        return None


def validate_email(email: str) -> bool:
    """Validate an email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate a phone number"""
    # Remove all non-digit characters
    digits_only = re.sub(r'[^\d+]', '', phone)

    # Check if it's a valid phone number
    # International format: +[country code][number]
    if digits_only.startswith('+') and len(digits_only) >= 8:
        return True

    # US format: 10 digits
    if len(digits_only) == 10:
        return True

    return False


def validate_domain(domain: str) -> bool:
    """Validate a domain name"""
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\$'
    return re.match(pattern, domain) is not None


def validate_ip(ip: str) -> bool:
    """Validate an IP address"""
    # IPv4
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\$'

    # IPv6 (simplified)
    ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\$'

    return (re.match(ipv4_pattern, ip) is not None or
            re.match(ipv6_pattern, ip) is not None)


def validate_url(url: str) -> bool:
    """Validate a URL"""
    pattern = r'^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\$'
    return re.match(pattern, url) is not None


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters (keep letters, numbers, spaces, and basic punctuation)
    text = re.sub(r'[^\w\s\-\.\,\:\;\!\?$$$$]', '', text)

    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


def format_date(date_str: str, input_format: str = "%Y-%m-%d", output_format: str = "%B %d, %Y") -> str:
    """Format a date string"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str


def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date"""
    try:
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date_obj.year

        # Adjust if birthday hasn't occurred yet this year
        if (today.month, today.day) < (birth_date_obj.month, birth_date_obj.day):
            age -= 1

        return age
    except ValueError:
        return 0


def mask_sensitive_data(text: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data, showing only the last few characters"""
    if len(text) <= visible_chars:
        return mask_char * len(text)

    return mask_char * (len(text) - visible_chars) + text[-visible_chars:]


def generate_api_key(length: int = 32) -> str:
    """Generate a random API key"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f}{size_names[i]}"


def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ""


def is_image_file(filename: str) -> bool:
    """Check if a file is an image"""
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    return get_file_extension(filename) in image_extensions


def is_document_file(filename: str) -> bool:
    """Check if a file is a document"""
    doc_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']
    return get_file_extension(filename) in doc_extensions


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Flatten a nested dictionary"""
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry a function on failure"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e

                    import time
                    time.sleep(delay)

            return None

        return wrapper

    return decorator


def rate_limit(calls: int, period: float):
    """Decorator to rate limit a function"""

    def decorator(func):
        last_called = [0.0]

        def wrapper(*args, **kwargs):
            import time
            now = time.time()
            elapsed = now - last_called[0]

            if elapsed < period / calls:
                time.sleep((period / calls) - elapsed)

            last_called[0] = time.time()
            return func(*args, **kwargs)

        return wrapper

    return decorator


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading and trailing spaces and dots
    filename = filename.strip(' .')

    # Ensure it's not empty
    if not filename:
        filename = "unnamed"

    return filename


def get_domain_from_email(email: str) -> str:
    """Extract domain from email address"""
    if validate_email(email):
        return email.split('@')[1]
    return ""


def get_username_from_email(email: str) -> str:
    """Extract username from email address"""
    if validate_email(email):
        return email.split('@')[0]
    return ""


def parse_user_agent(user_agent: str) -> Dict[str, str]:
    """Parse a user agent string"""
    # This is a simplified implementation
    result = {
        "browser": "Unknown",
        "os": "Unknown",
        "device": "Unknown"
    }

    # Browser detection
    if "Chrome" in user_agent:
        result["browser"] = "Chrome"
    elif "Firefox" in user_agent:
        result["browser"] = "Firefox"
    elif "Safari" in user_agent:
        result["browser"] = "Safari"
    elif "Edge" in user_agent:
        result["browser"] = "Edge"
    elif "Opera" in user_agent:
        result["browser"] = "Opera"

    # OS detection
    if "Windows" in user_agent:
        result["os"] = "Windows"
    elif "Mac OS" in user_agent or "macOS" in user_agent:
        result["os"] = "macOS"
    elif "Linux" in user_agent:
        result["os"] = "Linux"
    elif "Android" in user_agent:
        result["os"] = "Android"
    elif "iOS" in user_agent or "iPhone" in user_agent or "iPad" in user_agent:
        result["os"] = "iOS"

    # Device detection
    if "Mobile" in user_agent:
        result["device"] = "Mobile"
        elif "Tablet" in user_agent or "iPad" in user_agent:
        result["device"] = "Tablet"
    else:
        result["device"] = "Desktop"

    return result

    def calculate_password_strength(password: str) -> Dict[str, Any]:
        """Calculate password strength"""
        result = {
            "score": 0,
            "strength": "Very Weak",
            "feedback": []
        }

        # Length check
        if len(password) < 8:
            result["feedback"].append("Password should be at least 8 characters long")
        else:
            result["score"] += 1

        # Complexity checks
        if re.search(r'[a-z]', password):
            result["score"] += 1
        else:
            result["feedback"].append("Include lowercase letters")

        if re.search(r'[A-Z]', password):
            result["score"] += 1
        else:
            result["feedback"].append("Include uppercase letters")

        if re.search(r'[0-9]', password):
            result["score"] += 1
        else:
            result["feedback"].append("Include numbers")

        if re.search(r'[^a-zA-Z0-9]', password):
            result["score"] += 1
        else:
            result["feedback"].append("Include special characters")

        # Common patterns check
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            result["feedback"].append("Avoid repeated characters")
            result["score"] -= 1

        if re.search(r'123|abc|qwe|password', password.lower()):  # Common patterns
            result["feedback"].append("Avoid common patterns")
            result["score"] -= 1

        # Determine strength
        if result["score"] <= 2:
            result["strength"] = "Very Weak"
        elif result["score"] <= 3:
            result["strength"] = "Weak"
        elif result["score"] <= 4:
            result["strength"] = "Moderate"
        elif result["score"] <= 5:
            result["strength"] = "Strong"
        else:
            result["strength"] = "Very Strong"

        return result

    def generate_password(length: int = 12, include_symbols: bool = True) -> str:
        """Generate a random password"""
        characters = string.ascii_letters + string.digits

        if include_symbols:
            characters += "!@#\$%^&*()_+-=[]{}|;:,.<>?"

        return ''.join(random.choices(characters, k=length))

    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?'
        return re.findall(url_pattern, text)

    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)

    def extract_mentions(text: str) -> List[str]:
        """Extract mentions from text"""
        return re.findall(r'@\w+', text)

    def calculate_text_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple implementation)"""
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        # Remove punctuation and convert to lowercase
        cleaned_text = re.sub(r'[^\w\s]', '', text.lower())

        # Split into words
        words = cleaned_text.split()

        # Filter out common words (stopwords)
        stopwords = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our',
                     'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way',
                     'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']

        # Filter words by length and stopwords
        filtered_words = [word for word in words if len(word) >= min_length and word not in stopwords]

        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [word for word, _ in sorted_words[:max_keywords]]

    def detect_language(text: str) -> str:
        """Detect the language of text (simplified implementation)"""
        # This is a very simplified implementation
        # In a real implementation, you'd use a library like langdetect

        # Check for common words in different languages
        english_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had']
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se']
        french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir']
        german_words = ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
        russian_words = ['и', 'в', 'не', 'на', 'я', 'быть', 'он', 'с', 'что', 'а']

        text_lower = text.lower()

        # Count matches for each language
        english_count = sum(1 for word in english_words if word in text_lower)
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        french_count = sum(1 for word in french_words if word in text_lower)
        german_count = sum(1 for word in german_words if word in text_lower)
        russian_count = sum(1 for word in russian_words if word in text_lower)

        # Determine the most likely language
        language_counts = {
            'English': english_count,
            'Spanish': spanish_count,
            'French': french_count,
            'German': german_count,
            'Russian': russian_count
        }

        most_likely_language = max(language_counts, key=language_counts.get)

        # If no strong match, default to English
        if language_counts[most_likely_language] == 0:
            return 'English'

        return most_likely_language

    def extract_credit_card_numbers(text: str) -> List[str]:
        """Extract potential credit card numbers from text"""
        # This is a simplified pattern for demonstration
        # Real credit card validation would be more complex
        pattern = r'\b(?:\d[ -]*?){13,16}\b'
        matches = re.findall(pattern, text)

        # Clean up the results
        cleaned_cards = []
        for card in matches:
            # Remove spaces and dashes
            cleaned_card = re.sub(r'[ -]', '', card)

            # Check if it's a valid length for a credit card
            if len(cleaned_card) in [13, 15, 16]:
                cleaned_cards.append(cleaned_card)

        return cleaned_cards

    def validate_credit_card(number: str) -> bool:
        """Validate a credit card number using Luhn algorithm"""
        # Remove spaces and dashes
        number = re.sub(r'[ -]', '', number)

        # Check if it contains only digits
        if not number.isdigit():
            return False

        # Check length
        if len(number) not in [13, 15, 16]:
            return False

        # Luhn algorithm
        total = 0
        for i, digit in enumerate(number):
            digit = int(digit)

            if i % 2 == len(number) % 2:  # Every second digit from the right
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10

            total += digit

        return total % 10 == 0

    def get_credit_card_type(number: str) -> str:
        """Determine the type of credit card"""
        # Remove spaces and dashes
        number = re.sub(r'[ -]', '', number)

        # Visa
        if number.startswith('4'):
            return 'Visa'

        # MasterCard
        if number.startswith('5') and 51 <= int(number[1:3]) <= 55:
            return 'MasterCard'

        # American Express
        if number.startswith('34') or number.startswith('37'):
            return 'American Express'

            # Discover
            if number.startswith('6011') or (number.startswith('65') and 0 <= int(number[2:4]) <= 99) or (
                    number.startswith('644') and 0 <= int(number[3:6]) <= 999):
                return 'Discover'

            # Diners Club
            if (number.startswith('36') or number.startswith('38')) and len(number) == 14:
                return 'Diners Club'

            # JCB
            if number.startswith('35') and len(number) == 16:
                return 'JCB'

            return 'Unknown'

        def extract_social_security_numbers(text: str) -> List[str]:
            """Extract potential Social Security numbers from text"""
            # Pattern for SSN: XXX-XX-XXXX
            pattern = r'\b\d{3}-\d{2}-\d{4}\b'
            return re.findall(pattern, text)

        def validate_social_security_number(ssn: str) -> bool:
            """Validate a Social Security number"""
            # Check format
            if not re.match(r'^\d{3}-\d{2}-\d{4}\$', ssn):
                return False

            # Extract parts
            area, group, serial = ssn.split('-')

            # Check for invalid area numbers
            if area == '000' or area == '666' or int(area) >= 900:
                return False

            # Check for invalid group numbers
            if group == '00':
                return False

            # Check for invalid serial numbers
            if serial == '0000':
                return False

            return True

        def extract_ip_addresses(text: str) -> List[str]:
            """Extract IP addresses from text"""
            # IPv4 pattern
            ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

            # IPv6 pattern (simplified)
            ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'

            ips = re.findall(ipv4_pattern, text)
            ips.extend(re.findall(ipv6_pattern, text))

            return ips

        def validate_ip_address(ip: str) -> bool:
            """Validate an IP address"""
            # IPv4
            ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\$'

            # IPv6 (simplified)
            ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\$'

            return (re.match(ipv4_pattern, ip) is not None or
                    re.match(ipv6_pattern, ip) is not None)

        def extract_mac_addresses(text: str) -> List[str]:
            """Extract MAC addresses from text"""
            # Pattern for MAC addresses: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
            pattern = r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'
            return re.findall(pattern, text)

        def validate_mac_address(mac: str) -> bool:
            """Validate a MAC address"""
            # Pattern for MAC addresses: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
            pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\$'
            return re.match(pattern, mac) is not None

        def extract_dates(text: str) -> List[str]:
            """Extract dates from text"""
            # Various date patterns
            patterns = [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
                r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
                r'\b\d{4}/\d{1,2}/\d{1,2}\b',  # YYYY/MM/DD
                r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
                r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # D Month YYYY
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'  # Month D, YYYY
            ]

            dates = []
            for pattern in patterns:
                dates.extend(re.findall(pattern, text))

            return dates

        def extract_coordinates(text: str) -> List[str]:
            """Extract geographic coordinates from text"""
            # Pattern for coordinates: XX.XXXXX, -XX.XXXXX
            pattern = r'\b-?\d{1,3}\.\d+,\s*-?\d{1,3}\.\d+\b'
            return re.findall(pattern, text)

        def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate the distance between two coordinates in kilometers"""
            import math

            # Convert latitude and longitude to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))

            # Radius of Earth in kilometers
            r = 6371

            return c * r

        def extract_vehicle_identification_numbers(text: str) -> List[str]:
            """Extract VINs from text"""
            # Pattern for VINs: 17 characters (excluding I, O, Q)
            pattern = r'\b[A-HJ-NPR-Z0-9]{17}\b'
            return re.findall(pattern, text)

        def validate_vehicle_identification_number(vin: str) -> bool:
            """Validate a VIN"""
            # Check length
            if len(vin) != 17:
                return False

            # Check characters (VINs exclude I, O, Q)
            if re.search(r'[IOQ]', vin):
                return False

            # Check checksum (simplified)
            # Real VIN validation would be more complex
            return True

        def extract_passport_numbers(text: str) -> List[str]:
            """Extract passport numbers from text"""
            # This is a simplified pattern for demonstration
            # Real passport validation would depend on the country
            pattern = r'\b[A-Z]{1,2}\d{7,9}\b'
            return re.findall(pattern, text)

        def extract_driving_license_numbers(text: str) -> List[str]:
            """Extract driving license numbers from text"""
            # This is a simplified pattern for demonstration
            # Real license validation would depend on the state/country
            pattern = r'\b[A-Z0-9]{8,15}\b'
            return re.findall(pattern, text)

        def extract_bank_account_numbers(text: str) -> List[str]:
            """Extract bank account numbers from text"""
            # This is a simplified pattern for demonstration
            # Real account validation would depend on the bank/country
            pattern = r'\b(?:Account|Acct|Account No|Acct No)[:\s]*(\d{8,17})\b'
            matches = re.findall(pattern, text)

            # Also look for standalone numbers that could be account numbers
            if not matches:
                standalone_pattern = r'\b\d{10,17}\b'
                matches = re.findall(standalone_pattern, text)

            return matches

        def extract_routing_numbers(text: str) -> List[str]:
            """Extract bank routing numbers from text"""
            # Pattern for US routing numbers: 9 digits
            pattern = r'\b(?:Routing|RTN|ABA)[:\s]*(\d{9})\b'
            matches = re.findall(pattern, text)

            # Also look for standalone 9-digit numbers that could be routing numbers
            if not matches:
                standalone_pattern = r'\b\d{9}\b'
                matches = re.findall(standalone_pattern, text)

            return matches

        def validate_routing_number(routing_number: str) -> bool:
            """Validate a US bank routing number"""
            # Check length
            if len(routing_number) != 9:
                return False

            # Check if all digits
            if not routing_number.isdigit():
                return False

            # Validate using the standard checksum algorithm for routing numbers
            digits = [int(d) for d in routing_number]

            # Calculate checksum
            checksum = 0
            for i in range(9):
                if i % 3 == 0:
                    checksum += digits[i] * 3
                elif i % 3 == 1:
                    checksum += digits[i] * 7
                else:
                    checksum += digits[i]

            return checksum % 10 == 0

        def extract_iban_numbers(text: str) -> List[str]:
            """Extract IBAN numbers from text"""
            # Pattern for IBAN: country code (2 letters) + 2 digits + up to 30 alphanumeric characters
            pattern = r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b'
            return re.findall(pattern, text)

        def validate_iban(iban: str) -> bool:
            """Validate an IBAN number"""
            # Check length
            if len(iban) < 15 or len(iban) > 34:
                return False

            # Check format
            if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]+\$', iban):
                return False

            # Move the first four characters to the end
            rearranged = iban[4:] + iban[:4]

            # Replace letters with numbers (A=10, B=11, ..., Z=35)
            numeric = ''
            for char in rearranged:
                if char.isdigit():
                    numeric += char
                else:
                    numeric += str(ord(char) - ord('A') + 10)

            # Check if the numeric string is divisible by 97
            try:
                return int(numeric) % 97 == 1
            except ValueError:
                return False

        def extract_cryptocurrency_addresses(text: str) -> Dict[str, List[str]]:
            """Extract cryptocurrency addresses from text"""
            result = {
                "bitcoin": [],
                "ethereum": [],
                "litecoin": [],
                "ripple": [],
                "bitcoin_cash": [],
                "cardano": [],
                "polkadot": [],
                "dogecoin": []
            }

            # Bitcoin addresses: starting with 1, 3, or bc1
            btc_pattern = r'\b(?:1|3|bc1)[A-HJ-NP-Za-km-z1-9]{25,90}\b'
            result["bitcoin"] = re.findall(btc_pattern, text)

            # Ethereum addresses: 0x followed by 40 hex characters
            eth_pattern = r'\b0x[a-fA-F0-9]{40}\b'
            result["ethereum"] = re.findall(eth_pattern, text)

            # Litecoin addresses: starting with L, M, or 3
            ltc_pattern = r'\b[LM3][A-HJ-NP-Za-km-z1-9]{32,33}\b'
            result["litecoin"] = re.findall(ltc_pattern, text)

            # Ripple addresses: starting with r followed by 25-34 alphanumeric characters
            xrp_pattern = r'\br[A-HJ-NP-Za-km-z1-9]{25,34}\b'
            result["ripple"] = re.findall(xrp_pattern, text)

            # Bitcoin Cash addresses: starting with bitcoincash: or 1, 3, q
            bch_pattern1 = r'\bbitcoincash:[A-HJ-NP-Za-km-z1-9]{42}\b'
            bch_pattern2 = r'\b[13q][A-HJ-NP-Za-km-z1-9]{32,33}\b'
            result["bitcoin_cash"] = re.findall(bch_pattern1, text)
            result["bitcoin_cash"].extend(re.findall(bch_pattern2, text))

            # Cardano addresses: starting with addr1
            ada_pattern = r'\baddr1[A-Za-z0-9]{98}\b'
            result["cardano"] = re.findall(ada_pattern, text)

            # Polkadot addresses: starting with 1 followed by 47 hex characters
            dot_pattern = r'\b1[A-HJ-NP-Za-km-z1-9]{47}\b'
            result["polkadot"] = re.findall(dot_pattern, text)

            # Dogecoin addresses: starting with D
            doge_pattern = r'\bD[A-HJ-NP-Za-km-z1-9]{33}\b'
            result["dogecoin"] = re.findall(doge_pattern, text)

            return result

        def extract_stock_symbols(text: str) -> List[str]:
            """Extract stock symbols from text"""
            # Pattern for stock symbols: \$ followed by 1-5 uppercase letters
            pattern = r'\$[A-Z]{1,5}\b'
            return re.findall(pattern, text)

        def extract_isbn_numbers(text: str) -> List[str]:
            """Extract ISBN numbers from text"""
            # Pattern for ISBN-10 and ISBN-13
            isbn10_pattern = r'\b(?:ISBN[-\s]?10[:\s]?)?(\d{9}[\dXx])\b'
            isbn13_pattern = r'\b(?:ISBN[-\s]?13[:\s]?)?(97[89]\d{10})\b'

            isbn10 = re.findall(isbn10_pattern, text)
            isbn13 = re.findall(isbn13_pattern, text)

            return isbn10 + isbn13

        def validate_isbn(isbn: str) -> bool:
            """Validate an ISBN number"""
            # Remove any hyphens or spaces
            isbn = isbn.replace('-', '').replace(' ', '')

            # Check if it's ISBN-10
            if len(isbn) == 10:
                # Calculate checksum
                checksum = 0
                for i in range(9):
                    checksum += int(isbn[i]) * (10 - i)

                # Handle X as 10
                if isbn[9].upper() == 'X':
                    checksum += 10
                else:
                    checksum += int(isbn[9])

                return checksum % 11 == 0

            # Check if it's ISBN-13
            elif len(isbn) == 13:
                # Calculate checksum
                checksum = 0
                for i in range(12):
                    if i % 2 == 0:
                        checksum += int(isbn[i])
                    else:
                        checksum += int(isbn[i]) * 3

                checksum_digit = (10 - checksum % 10) % 10
                return checksum_digit == int(isbn[12])

            return False

        def extract_upc_codes(text: str) -> List[str]:
            """Extract UPC codes from text"""
            # Pattern for UPC-A: 12 digits
            upc_a_pattern = r'\b(\d{12})\b'

            # Pattern for UPC-E: 8 digits
            upc_e_pattern = r'\b(\d{8})\b'

            upc_a = re.findall(upc_a_pattern, text)
            upc_e = re.findall(upc_e_pattern, text)

            return upc_a + upc_e

        def validate_upc(upc: str) -> bool:
            """Validate a UPC code"""
            # Remove any hyphens or spaces
            upc = upc.replace('-', '').replace(' ', '')

            # Check length
            if len(upc) not in [8, 12]:
                return False

            # Check if all digits
            if not upc.isdigit():
                return False

            # Calculate checksum
            if len(upc) == 8:  # UPC-E
                # Convert UPC-E to UPC-A for checksum calculation
                if upc[6] in ['0', '1', '2']:
                    upc_a = upc[:3] + upc[6] + '0000' + upc[3:6] + upc[7]
                elif upc[6] == '3':
                    upc_a = upc[:3] + upc[6] + '00000' + upc[3:5] + upc[7]
                elif upc[6] == '4':
                    upc_a = upc[:3] + upc[6] + '00000' + upc[3:4] + upc[5] + upc[7]
                else:  # 5, 6, 7, 8, 9
                    upc_a = upc[:3] + upc[6] + upc[3:6] + '0000' + upc[7]
            else:  # UPC-A
                upc_a = upc

            # Calculate checksum for UPC-A
            checksum = 0
            for i in range(11):
                if i % 2 == 0:
                    checksum += int(upc_a[i])
                else:
                    checksum += int(upc_a[i]) * 3

            checksum_digit = (10 - checksum % 10) % 10
            return checksum_digit == int(upc_a[11])

        def extract_zip_codes(text: str) -> List[str]:
            """Extract ZIP codes from text"""
            # Pattern for US ZIP codes: 5 digits or 5-4 digits
            zip_pattern = r'\b(\d{5}(?:-\d{4})?)\b'
            return re.findall(zip_pattern, text)

        def extract_postal_codes(text: str) -> List[str]:
            """Extract postal codes from text (international)"""
            # This is a simplified pattern for demonstration
            # Real postal code validation would depend on the country

            # Canadian postal codes: A1A 1A1
            ca_pattern = r'\b[A-Z]\d[A-Z] ?\d[A-Z]\d\b'

            # UK postal codes: various formats
            uk_pattern = r'\b[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}\b'

            # German postal codes: 5 digits
            de_pattern = r'\b\d{5}\b'

            # French postal codes: 5 digits
            fr_pattern = r'\b\d{5}\b'

            # Japanese postal codes: 3-4 digits
            jp_pattern = r'\b\d{3}-\d{4}\b'

            # Australian postal codes: 4 digits
            au_pattern = r'\b\d{4}\b'

            # Find all matches
            ca_matches = re.findall(ca_pattern, text)
            uk_matches = re.findall(uk_pattern, text)
            de_matches = re.findall(de_pattern, text)
            fr_matches = re.findall(fr_pattern, text)
            jp_matches = re.findall(jp_pattern, text)
            au_matches = re.findall(au_pattern, text)

            # Combine all matches
            all_matches = ca_matches + uk_matches + de_matches + fr_matches + jp_matches + au_matches

            # Remove duplicates
            return list(set(all_matches))

        def extract_phone_numbers_with_country_code(text: str) -> List[Dict[str, str]]:
            """Extract phone numbers with country codes from text"""
            results = []

            # International format: +[country code][number]
            intl_pattern = r'\+(\d{1,3})([-\s]?)(\d{1,14})(?:[-\s]?)(\d{1,13})?'
            intl_matches = re.findall(intl_pattern, text)

            for match in intl_matches:
                country_code, sep1, number1, number2 = match
                number = f"{country_code}{sep1}{number1}"
                if number2:
                    number += f"{sep1}{number2}"

                results.append({
                    "country_code": f"+{country_code}",
                    "number": number,
                    "full": f"+{country_code}{sep1}{number1}{sep1 if number2 else ''}{number2 or ''}"
                })

            # US format: (XXX) XXX-XXXX or XXX-XXX-XXXX
            us_pattern = r'$$?(\d{3})$$?[-\s]?(\d{3})[-\s]?(\d{4})'
            us_matches = re.findall(us_pattern, text)

            for match in us_matches:
                area_code, prefix, line_number = match
                results.append({
                    "country_code": "+1",
                    "number": f"{area_code}{prefix}{line_number}",
                    "full": f"+1 ({area_code}) {prefix}-{line_number}"
                })

            return results

        def extract_company_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract company identification numbers from text"""
            results = []

            # EIN (Employer Identification Number): XX-XXXXXXX
            ein_pattern = r'\b(\d{2})-(\d{7})\b'
            ein_matches = re.findall(ein_pattern, text)

            for match in ein_matches:
                prefix, number = match
                results.append({
                    "type": "EIN",
                    "number": f"{prefix}-{number}"
                })

            # DUNS (Data Universal Numbering System): XX-XXX-XXXX
            duns_pattern = r'\b(\d{2})-(\d{3})-(\d{4})\b'
            duns_matches = re.findall(duns_pattern, text)

            for match in duns_matches:
                part1, part2, part3 = match
                results.append({
                    "type": "DUNS",
                    "number": f"{part1}-{part2}-{part3}"
                })

            # UK Company Number: Various formats
            uk_pattern = r'\b(?:Company No|Company Number|Co\. No)[:\s]*([A-Z0-9]{8})\b'
            uk_matches = re.findall(uk_pattern, text)

            for match in uk_matches:
                results.append({
                    "type": "UK Company Number",
                    "number": match
                })

            return results

        def extract_product_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract product identification numbers from text"""
            results = []

            # Serial numbers: Various formats
            serial_pattern = r'\b(?:S/N|Serial|Serial No|SN)[:\s]*([A-Z0-9-]{6,20})\b'
            serial_matches = re.findall(serial_pattern, text)

            for match in serial_matches:
                results.append({
                    "type": "Serial Number",
                    "number": match
                })

            # Model numbers: Various formats
            model_pattern = r'\b(?:Model|Model No|M/N)[:\s]*([A-Z0-9-]{4,20})\b'
            model_matches = re.findall(model_pattern, text)

            for match in model_matches:
                results.append({
                    "type": "Model Number",
                    "number": match
                })

            # Part numbers: Various formats
            part_pattern = r'\b(?:Part|Part No|P/N)[:\s]*([A-Z0-9-]{4,20})\b'
            part_matches = re.findall(part_pattern, text)

            for match in part_matches:
                results.append({
                    "type": "Part Number",
                    "number": match
                })

            return results

        def extract_medical_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract medical identification numbers from text"""
            results = []

            # NPI (National Provider Identifier): 10 digits
            npi_pattern = r'\b(?:NPI|National Provider Identifier)[:\s]*(\d{10})\b'
            npi_matches = re.findall(npi_pattern, text)

            for match in npi_matches:
                results.append({
                    "type": "NPI",
                    "number": match
                })

            # DEA (Drug Enforcement Administration) Number: 2 letters + 7 digits
            dea_pattern = r'\b(?:DEA|DEA No)[:\s]*([A-Z]{2}\d{7})\b'
            dea_matches = re.findall(dea_pattern, text)

            for match in dea_matches:
                results.append({
                    "type": "DEA",
                    "number": match
                })

            # Medical License Number: Various formats
            license_pattern = r'\b(?:Medical License|License No|Lic\. No)[:\s]*([A-Z0-9-]{6,20})\b'
            license_matches = re.findall(license_pattern, text)

            for match in license_matches:
                results.append({
                    "type": "Medical License",
                    "number": match
                })

            return results

        def extract_legal_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract legal identification numbers from text"""
            results = []

            # Bar Number: Various formats
            bar_pattern = r'\b(?:Bar No|Bar Number|Attorney No)[:\s]*([A-Z0-9-]{4,20})\b'
            bar_matches = re.findall(bar_pattern, text)

            for match in bar_matches:
                results.append({
                    "type": "Bar Number",
                    "number": match
                })

            # Case Number: Various formats
            case_pattern = r'\b(?:Case No|Case Number|Docket No)[:\s]*([A-Z0-9-]{4,20})\b'
            case_matches = re.findall(case_pattern, text)

            for match in case_matches:
                results.append({
                    "type": "Case Number",
                    "number": match
                })

            # Patent Number: Various formats
            patent_pattern = r'\b(?:Patent No|Patent Number)[:\s]*([A-Z0-9,]{4,20})\b'
            patent_matches = re.findall(patent_pattern, text)

            for match in patent_matches:
                results.append({
                    "type": "Patent Number",
                    "number": match
                })

            return results

        def extract_financial_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract financial identification numbers from text"""
            results = []

            # CUSIP (Committee on Uniform Securities Identification Procedures): 9 characters
            cusip_pattern = r'\b(?:CUSIP)[:\s]*([A-Z0-9]{9})\b'
            cusip_matches = re.findall(cusip_pattern, text)

            for match in cusip_matches:
                results.append({
                    "type": "CUSIP",
                    "number": match
                })

            # ISIN (International Securities Identification Number): 12 characters
            isin_pattern = r'\b(?:ISIN)[:\s]*([A-Z]{2}[A-Z0-9]{9}\d)\b'
            isin_matches = re.findall(isin_pattern, text)

            for match in isin_matches:
                results.append({
                    "type": "ISIN",
                    "number": match
                })

            # FIGI (Financial Instrument Global Identifier): 12 characters
            figi_pattern = r'\b(?:FIGI)[:\s]*([A-Z0-9]{12})\b'
            figi_matches = re.findall(figi_pattern, text)

            for match in figi_matches:
                results.append({
                    "type": "FIGI",
                    "number": match
                })

            return results

        def extract_educational_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract educational identification numbers from text"""
            results = []

            # Student ID: Various formats
            student_pattern = r'\b(?:Student ID|Student No|Student Number)[:\s]*([A-Z0-9-]{4,20})\b'
            student_matches = re.findall(student_pattern, text)

            for match in student_matches:
                results.append({
                    "type": "Student ID",
                    "number": match
                })

            # FAFSA (Free Application for Federal Student Aid) ID: 4 digits
            fafsa_pattern = r'\b(?:FAFSA|FAFSA ID)[:\s]*(\d{4})\b'
            fafsa_matches = re.findall(fafsa_pattern, text)

            for match in fafsa_matches:
                results.append({
                    "type": "FAFSA ID",
                    "number": match
                })

            # GED ID: Various formats
            ged_pattern = r'\b(?:GED|GED ID)[:\s]*([A-Z0-9-]{4,20})\b'
            ged_matches = re.findall(ged_pattern, text)

            for match in ged_matches:
                results.append({
                    "type": "GED ID",
                    "number": match
                })

            return results

        def extract_military_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract military identification numbers from text"""
            results = []

            # Service Number: Various formats
            service_pattern = r'\b(?:Service No|Service Number)[:\s]*([A-Z0-9-]{6,12})\b'
            service_matches = re.findall(service_pattern, text)

            for match in service_matches:
                results.append({
                    "type": "Service Number",
                    "number": match
                })

            # DoD ID Number: 10 digits
            dod_pattern = r'\b(?:DoD ID|DoD ID Number|Department of Defense ID)[:\s]*(\d{10})\b'
            dod_matches = re.findall(dod_pattern, text)

            for match in dod_matches:
                results.append({
                    "type": "DoD ID",
                    "number": match
                })

            # VA (Veterans Affairs) ID Number: Various formats
            va_pattern = r'\b(?:VA ID|VA ID Number|Veterans Affairs ID)[:\s]*([A-Z0-9-]{6,12})\b'
            va_matches = re.findall(va_pattern, text)

            for match in va_matches:
                results.append({
                    "type": "VA ID",
                    "number": match
                })

            return results

        def extract_transportation_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract transportation identification numbers from text"""
            results = []

            # Driver's License Number: Various formats
            license_pattern = r'\b(?:Driver\'s License|DL|License No|Lic\. No)[:\s]*([A-Z0-9-]{6,20})\b'
            license_matches = re.findall(license_pattern, text)

            for match in license_matches:
                results.append({
                    "type": "Driver's License",
                    "number": match
                })

            # Vehicle Registration Number: Various formats
            registration_pattern = r'\b(?:Vehicle Registration|Reg\. No|Registration No)[:\s]*([A-Z0-9-]{4,20})\b'
            registration_matches = re.findall(registration_pattern, text)

            for match in registration_matches:
                results.append({
                    "type": "Vehicle Registration",
                    "number": match
                })

            # License Plate Number: Various formats
            plate_pattern = r'\b(?:License Plate|Plate No|Plate)[:\s]*([A-Z0-9-]{2,10})\b'
            plate_matches = re.findall(plate_pattern, text)

            for match in plate_matches:
                results.append({
                    "type": "License Plate",
                    "number": match
                })

            return results

        def extract_telecommunication_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract telecommunication identification numbers from text"""
            results = []

            # IMEI (International Mobile Equipment Identity): 15 digits
            imei_pattern = r'\b(?:IMEI)[:\s]*(\d{15})\b'
            imei_matches = re.findall(imei_pattern, text)

            for match in imei_matches:
                results.append({
                    "type": "IMEI",
                    "number": match
                })

            # IMSI (International Mobile Subscriber Identity): 15 digits
            imsi_pattern = r'\b(?:IMSI)[:\s]*(\d{15})\b'
            imsi_matches = re.findall(imsi_pattern, text)

            for match in imsi_matches:
                results.append({
                    "type": "IMSI",
                    "number": match
                })

            # SIM Card Number: Various formats
            sim_pattern = r'\b(?:SIM|SIM Card|SIM No)[:\s]*([A-Z0-9-]{10,20})\b'
            sim_matches = re.findall(sim_pattern, text)

            for match in sim_matches:
                results.append({
                    "type": "SIM Card",
                    "number": match
                })

            return results

        def extract_utility_identification_numbers(text: str) -> List[Dict[str, str]]:
            """Extract utility identification numbers from text"""
            results = []

            # Account Number: Various formats
            account_pattern = r'\b(?:Account No|Account Number|Acct\. No)[:\s]*([A-Z0-9-]{6,20})\b'
            account_matches = re.findall(account_pattern, text)

            for match in account_matches:
                results.append({
                    "type": "Account Number",
                    "number": match
                })

            # Meter Number: Various formats
            meter_pattern = r'\b(?:Meter No|Meter Number)[:\s]*([A-Z0-9-]{4,20})\b'
            meter_matches = re.findall(meter_pattern, text)

            for match in meter_matches:
                results.append({
                    "type": "Meter Number",
                    "number": match
                })

            # Service Address: Various formats
            address_pattern = r'\b(?:Service Address|Service Location)[:\s]*([A-Z0-9\s,.-]{10,50})\b'
            address_matches = re.findall(address_pattern, text)

            for match in address_matches:
                results.append({
                    "type": "Service Address",
                    "number": match
                })

            return results

        def extract_all_identification_numbers(text: str) -> Dict[str, List[Dict[str, str]]]:
            """Extract all identification numbers from text"""
            return {
                "financial": extract_financial_identification_numbers(text),
                "medical": extract_medical_identification_numbers(text),
                "legal": extract_legal_identification_numbers(text),
                "educational": extract_educational_identification_numbers(text),
                "military": extract_military_identification_numbers(text),
                "transportation": extract_transportation_identification_numbers(text),
                "telecommunication": extract_telecommunication_identification_numbers(text),
                "utility": extract_utility_identification_numbers(text),
                "company": extract_company_identification_numbers(text),
                "product": extract_product_identification_numbers(text)
            }

        def validate_all_identification_numbers(data: Dict[str, List[Dict[str, str]]]) -> Dict[
            str, List[Dict[str, Any]]]:
            """Validate all identification numbers"""
            results = {}

            for category, items in data.items():
                results[category] = []

                for item in items:
                    result = {
                        "type": item["type"],
                        "number": item["number"],
                        "valid": False,
                        "error": None
                    }

                    try:
                        if category == "financial":
                            if item["type"] == "CUSIP":
                                result["valid"] = validate_cusip(item["number"])
                    elif item["type"] == "ISIN":
                    result["valid"] = validate_isin(item["number"])
                elif item["type"] == "FIGI":
                result["valid"] = validate_figi(item["number"])
            elif category == "medical":
            if item["type"] == "NPI":
                result["valid"] = validate_npi(item["number"])
            elif item["type"] == "DEA":
                result["valid"] = validate_dea(item["number"])

        elif category == "legal":
        if item["type"] == "Bar Number":
            result["valid"] = validate_bar_number(item["number"])
        elif item["type"] == "Case Number":
            result["valid"] = validate_case_number(item["number"])

    elif category == "educational":
    if item["type"] == "Student ID":
        result["valid"] = validate_student_id(item["number"])
    elif item["type"] == "FAFSA ID":
        result["valid"] = validate_fafsa_id(item["number"])

elif category == "military":
if item["type"] == "Service Number":
    result["valid"] = validate_service_number(item["number"])
elif item["type"] == "DoD ID":
    result["valid"] = validate_dod_id(item["number"])
elif category == "transportation":
    if item["type"] == "Driver's License":
        result["valid"] = validate_drivers_license(item["number"])
    elif item["type"] == "Vehicle Registration":
        result["valid"] = validate_vehicle_registration(item["number"])
    elif category == "telecommunication":
    if item["type"] == "IMEI":
        result["valid"] = validate_imei(item["number"])
    elif item["type"] == "IMSI":
        result["valid"] = validate_imsi(item["number"])
    elif category == "utility":
    if item["type"] == "Account Number":
        result["valid"] = validate_utility_account(item["number"])
    elif item["type"] == "Meter Number":
        result["valid"] = validate_meter_number(item["number"])
    elif category == "company":
    if item["type"] == "EIN":
        result["valid"] = validate_ein(item["number"])
    elif item["type"] == "DUNS":
        result["valid"] = validate_duns(item["number"])
    elif category == "product":
    if item["type"] == "Serial Number":
        result["valid"] = validate_serial_number(item["number"])
    elif item["type"] == "Model Number":
        result["valid"] = validate_model_number(item["number"])

if not result["valid"]:
    result["error"] = f"Invalid {item['type']} format"
except Exception as e:
result["error"] = str(e)

results[category].append(result)

return results


# Validation functions for specific identification numbers

def validate_cusip(cusip: str) -> bool:
    """Validate a CUSIP number"""
    # Check length
    if len(cusip) != 9:
        return False

    # Check characters
    if not re.match(r'^[A-Z0-9@#]{8}[0-9]\$', cusip):
        return False

    # Calculate checksum
    total = 0
    for i in range(8):
        char = cusip[i]

        if char.isdigit():
            value = int(char)
        elif char.isalpha():
            value = ord(char) - ord('A') + 10
        elif char == '@':
            value = 37
        elif char == '#':
            value = 38
        else:
            return False

        if i % 2 == 1:
            value *= 2

        total += value // 10 + value % 10

    checksum = (10 - (total % 10)) % 10
    return checksum == int(cusip[8])


def validate_isin(isin: str) -> bool:
    """Validate an ISIN number"""
    # Check length
    if len(isin) != 12:
        return False

    # Check format
    if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]\$', isin):
        return False

    # Move the first two characters to the end
    rearranged = isin[2:] + isin[:2]

    # Replace letters with numbers (A=10, B=11, ..., Z=35)
    numeric = ''
    for char in rearranged:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - ord('A') + 10)

    # Check if the numeric string is divisible by 97
    try:
        return int(numeric) % 97 == 1
    except ValueError:
        return False


def validate_figi(figi: str) -> bool:
    """Validate a FIGI number"""
    # Check length
    if len(figi) != 12:
        return False

    # Check characters
    if not re.match(r'^[A-Z0-9]{12}\$', figi):
        return False

    # First character should be 'B' for Bloomberg
    if figi[0] != 'B':
        return False

    # Second character should be 'G'
    if figi[1] != 'G':
        return False

    return True


def validate_npi(npi: str) -> bool:
    """Validate an NPI number"""
    # Check length
    if len(npi) != 10:
        return False

    # Check if all digits
    if not npi.isdigit():
        return False

    # Check if it starts with 1 or 2
    if npi[0] not in ['1', '2']:
        return False

    # Calculate checksum using Luhn algorithm with double and double+9
    total = 0
    for i in range(9):
        digit = int(npi[i])

        if i % 2 == 0:
            digit *= 2
            if digit > 9:
                digit = digit // 10 + digit % 10

        total += digit

    total += int(npi[9])

    return total % 10 == 0


def validate_dea(dea: str) -> bool:
    """Validate a DEA number"""
    # Check format
    if not re.match(r'^[A-Z]{2}\d{7}\$', dea):
        return False

    # Check second character
    if dea[1] not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'P', 'R', 'S', 'T', 'U', 'W', 'X',
                      'Y']:
        return False

    # Calculate checksum
    total = 0
    for i in range(2, 9):
        total += int(dea[i]) * (i - 1)

    remainder = total % 10

    if remainder == 0:
        checksum = 0
    else:
        checksum = 10 - remainder

    return checksum == int(dea[9])


def validate_bar_number(bar_number: str) -> bool:
    """Validate a bar number"""
    # This is a simplified validation
    # Real bar number validation would depend on the state

    # Check length
    if len(bar_number) < 4 or len(bar_number) > 20:
        return False

    # Check characters
    if not re.match(r'^[A-Z0-9-]+\$', bar_number):
        return False

    return True


def validate_case_number(case_number: str) -> bool:
    """Validate a case number"""
    # This is a simplified validation
    # Real case number validation would depend on the jurisdiction

    # Check length
    if len(case_number) < 4 or len(case_number) > 20:
        return False

    # Check characters
    if not re.match(r'^[A-Z0-9-]+\$', case_number):
        return False

    return True


def validate_student_id(student_id: str) -> bool:
    """Validate a student ID"""
    # This is a simplified validation
    # Real student ID validation would depend on the institution

    # Check length
    if len(student_id) < 4 or len(student_id) > 20:
        return False

    # Check characters
    if not re.match(r'^[A-Z0-9-]+\$', student_id):
        return False

    return True


def validate_fafsa_id(fafsa_id: str) -> bool:
    """Validate a FAFSA ID"""
    # Check length
    if len(fafsa_id) != 4:
        return False

    # Check if all digits
    if not fafsa_id.isdigit():
        return False

    return True


def validate_service_number(service_number: str) -> bool:
    """Validate a service number"""
    # This is a simplified validation
    # Real service number validation would depend on the branch of service

    # Check length
    if len(service_number) < 6 or len(service_number) > 12:
        return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', service_number):
            return False

        return True

    def validate_dod_id(dod_id: str) -> bool:
        """Validate a DoD ID number"""
        # Check length
        if len(dod_id) != 10:
            return False

        # Check if all digits
        if not dod_id.isdigit():
            return False

        return True

    def validate_drivers_license(license_number: str) -> bool:
        """Validate a driver's license number"""
        # This is a simplified validation
        # Real driver's license validation would depend on the state

        # Check length
        if len(license_number) < 6 or len(license_number) > 20:
            return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', license_number):
            return False

        return True

    def validate_vehicle_registration(registration_number: str) -> bool:
        """Validate a vehicle registration number"""
        # This is a simplified validation
        # Real vehicle registration validation would depend on the state

        # Check length
        if len(registration_number) < 4 or len(registration_number) > 20:
            return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', registration_number):
            return False

        return True

    def validate_imei(imei: str) -> bool:
        """Validate an IMEI number"""
        # Check length
        if len(imei) != 15:
            return False

        # Check if all digits
        if not imei.isdigit():
            return False

        # Calculate checksum using Luhn algorithm
        total = 0
        for i in range(14):
            digit = int(imei[i])

            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10

            total += digit

        checksum = (10 - (total % 10)) % 10
        return checksum == int(imei[14])

    def validate_imsi(imsi: str) -> bool:
        """Validate an IMSI number"""
        # Check length
        if len(imsi) != 15:
            return False

        # Check if all digits
        if not imsi.isdigit():
            return False

        # Check MCC (Mobile Country Code) - first 3 digits
        mcc = int(imsi[:3])
        if mcc < 100 or mcc > 999:
            return False

        # Check MNC (Mobile Network Code) - next 2-3 digits
        mnc_length = 2  # Default
        if mcc in [302, 310, 311, 316, 338, 342, 344, 346, 348, 365, 374, 376, 404, 405, 406, 410, 413, 415, 416, 417,
                   418, 419, 420, 421, 422, 424, 425, 426, 427, 428, 429, 430, 431, 432, 434, 436, 437, 438, 440, 441,
                   452, 454, 455, 456, 457, 460, 461, 466, 467, 470, 472, 502, 505, 510, 514, 515, 520, 525, 528, 530,
                   536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555,
                   602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621,
                   622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641,
                   642, 643, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 657, 658, 659, 702, 704, 706, 708,
                   710, 712, 714, 716, 722, 724, 730, 732, 734, 736, 738, 740, 742, 744, 746, 748, 750, 752, 754, 756,
                   758, 760, 762, 764, 766, 768, 770, 772, 774, 776, 778, 780, 782, 784, 786, 788, 790, 792, 794, 796,
                   798, 901, 902]:
            mnc_length = 3

        mnc = int(imsi[3:3 + mnc_length])
        if mnc < 10 or mnc > 999:
            return False

        return True

    def validate_utility_account(account_number: str) -> bool:
        """Validate a utility account number"""
        # This is a simplified validation
        # Real utility account validation would depend on the utility company

        # Check length
        if len(account_number) < 6 or len(account_number) > 20:
            return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', account_number):
            return False

        return True

    def validate_meter_number(meter_number: str) -> bool:
        """Validate a meter number"""
        # This is a simplified validation
        # Real meter number validation would depend on the utility company

        # Check length
        if len(meter_number) < 4 or len(meter_number) > 20:
            return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', meter_number):
            return False

        return True

    def validate_ein(ein: str) -> bool:
        """Validate an EIN number"""
        # Check format
        if not re.match(r'^\d{2}-\d{7}$', ein):
            return False

        # Check prefix
        prefix = ein[:2]
        if prefix in ['00', '07', '08', '09', '17', '18', '19', '28', '29', '49', '69', '70', '78', '79', '89', '96',
                      '97']:
            return False

        return True

    def validate_duns(duns: str) -> bool:
        """Validate a DUNS number"""
        # Check format
        if not re.match(r'^\d{2}-\d{3}-\d{4}$', duns):
            return False

        # Remove hyphens
        digits = duns.replace('-', '')

        # Check if all digits
        if not digits.isdigit():
            return False

        return True

    def validate_serial_number(serial_number: str) -> bool:
        """Validate a serial number"""
        # This is a simplified validation
        # Real serial number validation would depend on the manufacturer

        # Check length
        if len(serial_number) < 6 or len(serial_number) > 20:
            return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', serial_number):
            return False

        return True

    def validate_model_number(model_number: str) -> bool:
        """Validate a model number"""
        # This is a simplified validation
        # Real model number validation would depend on the manufacturer

        # Check length
        if len(model_number) < 4 or len(model_number) > 20:
            return False

        # Check characters
        if not re.match(r'^[A-Z0-9-]+$', model_number):
            return False

        return True