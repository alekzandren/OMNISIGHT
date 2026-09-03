# OMNISIGHT - OSINT-Investigator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg?style=flat-square)](https://github.com/your-username/osint-investigator)
[![Version](https://img.shields.io/badge/Version-1.0.0-blueviolet.svg?style=flat-square)](https://github.com/your-username/osint-investigator)
[![Security: OSINT](https://img.shields.io/badge/Security-OSINT%20Tool-red.svg?style=flat-square)](https://owasp.org/www-project-owasp-internet-of-things/)
[![Powered by: Scrapy](https://img.shields.io/badge/Powered%20by-Scrapy%20%7C%20Selenium%20%7C%20Playwright-green.svg?style=flat-square)](https://scrapy.org/)

An advanced, comprehensive Python-based investigation tool designed for OSINT (Open-Source Intelligence) gathering, digital forensics, and security research. Built with a modular architecture and multiple data collection engines including Scrapy, Selenium, and Playwright for comprehensive digital investigations.

## Key Features

* **Modular Architecture**: Formulated around a class-based design with separate modules for different investigation domains (darknet, leaks, social media, network analysis)
* **Multi-Engine Data Collection**: Powered by Scrapy, Selenium, and Playwright for comprehensive web scraping and automation
* **Advanced Document Analysis**: Supports PDF, DOCX, and Excel file analysis with PyPDF2, python-docx, and openpyxl
* **Comprehensive Reporting**: Dynamic report generation with Jinja2 templates and export to multiple formats (PDF, HTML, Excel)
* **Network Intelligence**: Built-in network scanning with python-nmap and scapy for infrastructure analysis
* **Security & Anonymity**: Tor support with stem, proxy rotation, and encrypted communications
* **Data Integration**: SQLAlchemy, aiosqlite, and MongoDB support for efficient data storage and retrieval
* **Rich Visualization**: Matplotlib and Plotly integration for data visualization and analysis

---

## Core Modules

| Module | Purpose | Key Technologies |
| :--- | :--- | :--- |
| `darknet_scanner.py` | Dark web investigation | Tor, stem, requests[socks] |
| `leak_scanner.py` | Data breach analysis | haveibeenpwned, cryptography |
| `social_scraper.py` | Social media intelligence | tweepy, selenium, playwright |
| `network_analyzer.py` | Network reconnaissance | python-nmap, scapy |
| `document_analyzer.py` | Document forensics | PyPDF2, python-docx, openpyxl |
| `identity_processor.py` | Identity correlation | pandas, numpy, cryptography |
| `migration_checker.py` | Data movement tracking | sqlalchemy, pymongo |

---

## Installation & Setup

### Prerequisites
* **Python 3.8+**
* `pip` or `poetry`
* PostgreSQL/MongoDB (optional, for data storage)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/osint-investigator.git
cd osint-investigator
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a file in the root directory of the project: `.env`
```env
# Database Configuration
DATABASE_URL=sqlite:///./investigation.db
MONGODB_URL=mongodb://localhost:27017/investigation_db

# API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# Tor Configuration
TOR_PROXY=socks5://127.0.0.1:9050
TOR_CONTROL_PORT=9051

# Report Configuration
REPORT_OUTPUT_DIR=./reports
TEMPLATE_DIR=./reports/templates

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/investigation.log
```

---

## Usage
Run the main investigator application:
```bash
python main.py
```

### Example Commands
```bash
# Scan for leaked credentials
python main.py --module leak_scanner --email example@domain.com

# Analyze social media presence
python main.py --module social_scraper --target username

# Network reconnaissance
python main.py --module network_analyzer --target 192.168.1.1

# Generate comprehensive report
python main.py --module report_generator --case_id 12345 --format pdf
```

### Example Output
```plaintext
2026-09-03 12:00:01 - [INFO] - Starting OSINT tool for investigation
2026-09-03 12:00:02 - [INFO] - Module leak_scanner: Searching for leaks for example@domain.com
2026-09-03 12:00:05 - [WARNING] - [FOUND] Leak detected in service X (2023-05-12)
2026-09-03 12:00:08 - [INFO] - Module social_scraper: Analyzing profile username
2026-09-03 12:00:15 - [INFO] - [FOUND] 3 social networks detected: Twitter, LinkedIn, Instagram
2026-09-03 12:00:20 - [INFO] - Generating report for case_id 12345
2026-09-03 12:00:25 - [SUCCESS] - Report saved to ./reports/case_12345_20260903.pdf
```

---

## Security Disclaimer
**Disclaimer**: This tool is developed strictly for authorized security research, digital forensics, and educational purposes. Using this tool for unauthorized access to computer systems or for illegal activities is prohibited. The author holds no liability for misuse or damage caused by this program.

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

