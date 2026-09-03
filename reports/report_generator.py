import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
import pdfkit
import json

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Module for generating investigation reports"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Initialize Jinja2 environment
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        os.makedirs(self.template_dir, exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))

        # Create default templates if they don't exist
        self._create_default_templates()

    def _create_default_templates(self):
        """Create default report templates if they don't exist"""
        # HTML template
        html_template_path = os.path.join(self.template_dir, "report.html")
        if not os.path.exists(html_template_path):
            with open(html_template_path, "w") as f:
                f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniSight Investigation Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        h1 {
            color: #333;
            margin: 0;
        }
        .summary {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .section {
            margin-bottom: 30px;
        }
        h2 {
            color: #444;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        h3 {
            color: #555;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        .data-item {
            margin-bottom: 15px;
            padding: 10px;
            border: 1px solid #eee;
            border-radius: 5px;
        }
        .data-item h4 {
            margin-top: 0;
            color: #444;
        }
        .label {
            font-weight: bold;
            display: inline-block;
            width: 120px;
        }
        .value {
            display: inline-block;
        }
        .error {
            color: #d9534f;
        }
        .warning {
            color: #f0ad4e;
        }
        .success {
            color: #5cb85c;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>OmniSight Investigation Report</h1>
            <p>Generated on {{ report_date }}</p>
        </header>

        <div class="summary">
            <h2>Executive Summary</h2>
            <p><strong>Query:</strong> {{ query }}</p>
            <p><strong>Data Type:</strong> {{ data_type }}</p>
            <p><strong>Total Sources Checked:</strong> {{ total_sources }}</p>
            <p><strong>Results Found:</strong> {{ total_results }}</p>
        </div>

        {% if email_results %}
        <div class="section">
            <h2>Email Analysis</h2>
            {% for result in email_results %}
            <div class="data-item">
                <h4>{{ result.get('domain', result.get('email', 'Unknown')) }}</h4>
                {% if result.get('valid', True) %}
                {% if result.get('domain') %}
                <p><span class="label">Domain:</span> <span class="value">{{ result.domain }}</span></p>
                <p><span class="label">Registrar:</span> <span class="value">{{ result.whois.get('registrar', 'Unknown') }}</span></p>
                <p><span class="label">Created:</span> <span class="value">{{ result.whois.get('creation_date', 'Unknown') }}</span></p>
                <p><span class="label">Expires:</span> <span class="value">{{ result.whois.get('expiry_date', 'Unknown') }}</span></p>
                {% if result.get('security') %}
                <p><span class="label">Reputation:</span> <span class="value {{ 'error' if result.security.reputation == 'malicious' else 'warning' if result.security.reputation == 'suspicious' else 'success' }}">{{ result.security.reputation }}</span></p>
                {% endif %}
                {% if result.get('subdomains') %}
                <p><span class="label">Subdomains:</span> <span class="value">{{ result.subdomains|length }} found</span></p>
                {% endif %}
                {% endif %}
                {% if result.get('emails') %}
                <p><span class="label">Emails:</span> <span class="value">{{ result.emails|length }} found</span></p>
                {% endif %}
                {% if result.get('breaches') %}
                <p><span class="label">Breaches:</span> <span class="value">{{ result.breaches|length }} found</span></p>
                {% endif %}
                {% if result.get('social_accounts') %}
                <p><span class="label">Social Accounts:</span> <span class="value">{{ result.social_accounts|length }} found</span></p>
                {% endif %}
                {% else %}
                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if phone_results %}
        <div class="section">
            <h2>Phone Analysis</h2>
            {% for result in phone_results %}
            <div class="data-item">
                <h4>{{ result.get('phone', 'Unknown') }}</h4>
                {% if result.get('valid', True) %}
                {% if result.get('carrier') %}
                <p><span class="label">Carrier:</span> <span class="value">{{ result.carrier }}</span></p>
                <p><span class="label">Country:</span> <span class="value">{{ result.country }}</span></p>
                <p><span class="label">Type:</span> <span class="value">{{ result.type }}</span></p>
                {% endif %}
                {% if result.get('location') %}
                <p><span class="label">Location:</span> <span class="value">{{ result.location.city }}, {{ result.location.region }}, {{ result.location.country }}</span></p>
                                {% endif %}
                                {% if result.get('social_accounts') %}
                                <p><span class="label">Social Accounts:</span> <span class="value">{{ result.social_accounts|length }} found</span></p>
                                {% endif %}
                                {% if result.get('leaks') %}
                                <p><span class="label">Data Leaks:</span> <span class="value">{{ result.leaks|length }} found</span></p>
                                {% endif %}
                                {% else %}
                                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if name_results %}
                        <div class="section">
                            <h2>Name Analysis</h2>
                            {% for result in name_results %}
                            <div class="data-item">
                                <h4>{{ result.get('name', 'Unknown') }}</h4>
                                {% if result.get('valid', True) %}
                                {% if result.get('age') %}
                                <p><span class="label">Age:</span> <span class="value">{{ result.age }}</span></p>
                                {% endif %}
                                {% if result.get('location') %}
                                <p><span class="label">Location:</span> <span class="value">{{ result.location.city }}, {{ result.location.state }}, {{ result.location.country }}</span></p>
                                {% endif %}
                                {% if result.get('relatives') %}
                                <p><span class="label">Relatives:</span> <span class="value">{{ result.relatives|length }} found</span></p>
                                {% endif %}
                                {% if result.get('associates') %}
                                <p><span class="label">Associates:</span> <span class="value">{{ result.associates|length }} found</span></p>
                                {% endif %}
                                {% if result.get('social_profiles') %}
                                <p><span class="label">Social Profiles:</span> <span class="value">{{ result.social_profiles|length }} found</span></p>
                                {% endif %}
                                {% else %}
                                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if username_results %}
                        <div class="section">
                            <h2>Username Analysis</h2>
                            {% for result in username_results %}
                            <div class="data-item">
                                <h4>{{ result.get('username', 'Unknown') }}</h4>
                                {% if result.get('valid', True) %}
                                {% if result.get('platforms') %}
                                <p><span class="label">Platforms:</span> <span class="value">{{ result.platforms|length }} found</span></p>
                                {% endif %}
                                {% if result.get('profile_data') %}
                                <p><span class="label">Profile Data:</span> <span class="value">Available</span></p>
                                {% endif %}
                                {% else %}
                                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if domain_results %}
                        <div class="section">
                            <h2>Domain Analysis</h2>
                            {% for result in domain_results %}
                            <div class="data-item">
                                <h4>{{ result.get('domain', 'Unknown') }}</h4>
                                {% if result.get('valid', True) %}
                                {% if result.get('whois') %}
                                <p><span class="label">Registrar:</span> <span class="value">{{ result.whois.get('registrar', 'Unknown') }}</span></p>
                                <p><span class="label">Created:</span> <span class="value">{{ result.whois.get('creation_date', 'Unknown') }}</span></p>
                                <p><span class="label">Expires:</span> <span class="value">{{ result.whois.get('expiry_date', 'Unknown') }}</span></p>
                                {% endif %}
                                {% if result.get('dns') %}
                                <p><span class="label">DNS Records:</span> <span class="value">Available</span></p>
                                {% endif %}
                                {% if result.get('security') %}
                                <p><span class="label">Reputation:</span> <span class="value {{ 'error' if result.security.reputation == 'malicious' else 'warning' if result.security.reputation == 'suspicious' else 'success' }}">{{ result.security.reputation }}</span></p>
                                {% endif %}
                                {% if result.get('subdomains') %}
                                <p><span class="label">Subdomains:</span> <span class="value">{{ result.subdomains|length }} found</span></p>
                                {% endif %}
                                {% if result.get('emails') %}
                                <p><span class="label">Emails:</span> <span class="value">{{ result.emails|length }} found</span></p>
                                {% endif %}
                                {% else %}
                                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if ip_results %}
                        <div class="section">
                            <h2>IP Analysis</h2>
                            {% for result in ip_results %}
                            <div class="data-item">
                                <h4>{{ result.get('ip', 'Unknown') }}</h4>
                                {% if result.get('valid', True) %}
                                {% if result.get('location') %}
                                <p><span class="label">Location:</span> <span class="value">{{ result.location.city }}, {{ result.location.region }}, {{ result.location.country }}</span></p>
                                {% endif %}
                                {% if result.get('isp') %}
                                <p><span class="label">ISP:</span> <span class="value">{{ result.isp.isp }}</span></p>
                                {% endif %}
                                {% if result.get('security') %}
                                <p><span class="label">Reputation:</span> <span class="value {{ 'error' if result.security.reputation == 'malicious' else 'warning' if result.security.reputation == 'suspicious' else 'success' }}">{{ result.security.reputation }}</span></p>
                                {% endif %}
                                {% if result.get('domains') %}
                                <p><span class="label">Domains:</span> <span class="value">{{ result.domains|length }} found</span></p>
                                {% endif %}
                                {% else %}
                                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if darknet_results %}
                        <div class="section">
                            <h2>Darknet Analysis</h2>
                            {% for result in darknet_results %}
                            <div class="data-item">
                                <h4>{{ result.get('source', 'Unknown') }}</h4>
                                <p><span class="label">Type:</span> <span class="value">{{ result.get('type', 'Unknown') }}</span></p>
                                <p><span class="label">Content:</span> <span class="value">{{ result.get('content', 'No content available') }}</span></p>
                                <p><span class="label">Date:</span> <span class="value">{{ result.get('date', 'Unknown') }}</span></p>
                                <p><span class="label">Context:</span> <span class="value">{{ result.get('context', 'No context available') }}</span></p>
                                <p><span class="label">Relevance:</span> <span class="value">{{ result.get('relevance', 0) }}/10</span></p>
                                {% if result.get('url') %}
                                <p><span class="label">URL:</span> <span class="value">{{ result.url }}</span></p>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if leak_results %}
                        <div class="section">
                            <h2>Leak Analysis</h2>
                            {% for result in leak_results %}
                            <div class="data-item">
                                <h4>{{ result.get('source', 'Unknown') }}</h4>
                                <p><span class="label">Date:</span> <span class="value">{{ result.get('date', 'Unknown') }}</span></p>
                                <p><span class="label">Description:</span> <span class="value">{{ result.get('description', 'No description available') }}</span></p>
                                <p><span class="label">Data Classes:</span> <span class="value">{{ result.get('data_classes', [])|join(', ') }}</span></p>
                                <p><span class="label">Records:</span> <span class="value">{{ result.get('records_count', 0) }}</span></p>
                                <p><span class="label">Verified:</span> <span class="value {{ 'success' if result.get('verified') else 'warning' }}">{{ 'Yes' if result.get('verified') else 'No' }}</span></p>
<p><span class="label">Context:</span> <span class="value">{{ result.get('context', 'No context available') }}</span></p>
                {% if result.get('url') %}
                <p><span class="label">URL:</span> <span class="value">{{ result.url }}</span></p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if document_results %}
        <div class="section">
            <h2>Document Analysis</h2>
            {% for result in document_results %}
            <div class="data-item">
                <h4>{{ result.get('document', {}).get('document_type', 'Unknown') }}</h4>
                {% if result.get('valid', True) %}
                {% if result.get('document') %}
                <p><span class="label">Document Number:</span> <span class="value">{{ result.document.get('document_number', 'Unknown') }}</span></p>
                <p><span class="label">Name:</span> <span class="value">{{ result.document.get('first_name', '') }} {{ result.document.get('last_name', '') }}</span></p>
                <p><span class="label">Date of Birth:</span> <span class="value">{{ result.document.get('date_of_birth', 'Unknown') }}</span></p>
                <p><span class="label">Issue Date:</span> <span class="value">{{ result.document.get('issue_date', 'Unknown') }}</span></p>
                <p><span class="label">Expiry Date:</span> <span class="value">{{ result.document.get('expiry_date', 'Unknown') }}</span></p>
                <p><span class="label">Issuing Authority:</span> <span class="value">{{ result.document.get('issuing_authority', 'Unknown') }}</span></p>
                {% endif %}
                <p><span class="label">Confidence:</span> <span class="value">{{ "%.2f"|format(result.get('confidence', 0)) }}</span></p>
                {% else %}
                <p class="error">{{ result.get('error', 'Unknown error') }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <footer>
            <p>Report generated by OmniSight on {{ report_date }}</p>
            <p>This report contains sensitive information and should be handled securely.</p>
        </footer>
    </div>
</body>
</html>
                """)

        # JSON template
        json_template_path = os.path.join(self.template_dir, "report.json")
        if not os.path.exists(json_template_path):
            with open(json_template_path, "w") as f:
                f.write("""
{
    "report_metadata": {
        "generated_on": "{{ report_date }}",
        "query": "{{ query }}",
        "data_type": "{{ data_type }}",
        "total_sources": {{ total_sources }},
        "total_results": {{ total_results }}
    },
    "results": {
        {% if email_results %}"email": {{ email_results|tojson }},{% endif %}
        {% if phone_results %}"phone": {{ phone_results|tojson }},{% endif %}
        {% if name_results %}"name": {{ name_results|tojson }},{% endif %}
        {% if username_results %}"username": {{ username_results|tojson }},{% endif %}
        {% if domain_results %}"domain": {{ domain_results|tojson }},{% endif %}
        {% if ip_results %}"ip": {{ ip_results|tojson }},{% endif %}
        {% if darknet_results %}"darknet": {{ darknet_results|tojson }},{% endif %}
        {% if leak_results %}"leaks": {{ leak_results|tojson }},{% endif %}
        {% if document_results %}"documents": {{ document_results|tojson }}{% endif %}
    }
}
                """)

    async def generate_report(
            self,
            query: str,
            data_type: str,
            results: Dict[str, List[Dict[str, Any]]],
            output_format: str = "html",
            output_filename: Optional[str] = None
    ) -> str:
        """Generate an investigation report"""
        logger.info(f"Generating {output_format} report for {data_type}: {query}")

        # Calculate total sources and results
        total_sources = len(results.keys())
        total_results = sum(len(r) for r in results.values())

        # Generate filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"report_{data_type}_{timestamp}"

        # Prepare template variables
        template_vars = {
            "query": query,
            "data_type": data_type,
            "total_sources": total_sources,
            "total_results": total_results,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **results
        }

        # Generate report based on format
        if output_format == "html":
            output_path = os.path.join(self.output_dir, f"{output_filename}.html")
            await self._generate_html_report(template_vars, output_path)
        elif output_format == "pdf":
            output_path = os.path.join(self.output_dir, f"{output_filename}.pdf")
            await self._generate_pdf_report(template_vars, output_path)
        elif output_format == "json":
            output_path = os.path.join(self.output_dir, f"{output_filename}.json")
            await self._generate_json_report(template_vars, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        logger.info(f"Report generated: {output_path}")
        return output_path

    async def _generate_html_report(self, template_vars: Dict[str, Any], output_path: str):
        """Generate an HTML report"""
        template = self.jinja_env.get_template("report.html")
        html_content = template.render(**template_vars)

        with open(output_path, "w") as f:
            f.write(html_content)

    async def _generate_pdf_report(self, template_vars: Dict[str, Any], output_path: str):
        """Generate a PDF report"""
        # First generate HTML
        template = self.jinja_env.get_template("report.html")
        html_content = template.render(**template_vars)

        # Convert HTML to PDF
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }

        pdfkit.from_string(html_content, output_path, options=options)

    async def _generate_json_report(self, template_vars: Dict[str, Any], output_path: str):
        """Generate a JSON report"""
        template = self.jinja_env.get_template("report.json")
        json_content = template.render(**template_vars)

        # Parse the rendered JSON to ensure it's valid
        parsed_json = json.loads(json_content)

        with open(output_path, "w") as f:
            json.dump(parsed_json, f, indent=2)

    async def generate_summary_report(
            self,
            query: str,
            data_type: str,
            results: Dict[str, List[Dict[str, Any]]],
            output_filename: Optional[str] = None
    ) -> str:
        """Generate a summary report with key findings"""
        logger.info(f"Generating summary report for {data_type}: {query}")

        # Generate filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"summary_{data_type}_{timestamp}"

        output_path = os.path.join(self.output_dir, f"{output_filename}.txt")

        # Calculate total sources and results
        total_sources = len(results.keys())
        total_results = sum(len(r) for r in results.values())

        # Generate summary content
        with open(output_path, "w") as f:
            f.write("OMNISIGHT INVESTIGATION SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Query: {query}\n")
            f.write(f"Data Type: {data_type}\n")
            f.write(f"Total Sources Checked: {total_sources}\n")
            f.write(f"Total Results Found: {total_results}\n\n")

            # Summarize each category
            for category, category_results in results.items():
                if category_results:
                    f.write(f"{category.upper()} ANALYSIS:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Results Found: {len(category_results)}\n")

                    # Add key findings for each result
                    for result in category_results[:3]:  # Limit to top 3 results
                        if result.get('valid', True):
                            if category == "email":
                                f.write(f"- {result.get('domain', result.get('email', 'Unknown'))}")
                                if result.get('security'):
                                    f.write(f" (Reputation: {result.security.reputation})")
                                if result.get('breaches'):
                                    f.write(f" (Breaches: {len(result.breaches)})")
                                elif category == "phone":
                                    f.write(f"- {result.get('phone', 'Unknown')}")
                                    if result.get('carrier'):
                                        f.write(f" (Carrier: {result.carrier})")
                                    if result.get('leaks'):
                                        f.write(f" (Data Leaks: {len(result.leaks)})")
                                elif category == "name":
                                    f.write(f"- {result.get('name', 'Unknown')}")
                                    if result.get('age'):
                                        f.write(f" (Age: {result.age})")
                                    if result.get('location'):
                                        f.write(f" (Location: {result.location.city}, {result.location.state})")
                                elif category == "username":
                                    f.write(f"- {result.get('username', 'Unknown')}")
                                    if result.get('platforms'):
                                        f.write(f" (Platforms: {len(result.platforms)})")
                                elif category == "domain":
                                    f.write(f"- {result.get('domain', 'Unknown')}")
                                    if result.get('security'):
                                        f.write(f" (Reputation: {result.security.reputation})")
                                    if result.get('subdomains'):
                                        f.write(f" (Subdomains: {len(result.subdomains)})")
                                elif category == "ip":
                                    f.write(f"- {result.get('ip', 'Unknown')}")
                                    if result.get('location'):
                                        f.write(f" (Location: {result.location.city}, {result.location.country})")
                                    if result.get('security'):
                                        f.write(f" (Reputation: {result.security.reputation})")
                                elif category == "darknet":
                                    f.write(f"- {result.get('source', 'Unknown')}")
                                    f.write(f" (Type: {result.get('type', 'Unknown')})")
                                    f.write(f" (Relevance: {result.get('relevance', 0)}/10)")
                                elif category == "leaks":
                                    f.write(f"- {result.get('source', 'Unknown')}")
                                    f.write(f" (Date: {result.get('date', 'Unknown')})")
                                    f.write(f" (Records: {result.get('records_count', 0)})")
                                    f.write(f" (Verified: {'Yes' if result.get('verified') else 'No'})")
                                elif category == "documents":
                                    f.write(f"- {result.get('document', {}).get('document_type', 'Unknown')}")
                                    f.write(
                                        f" (Name: {result.document.get('first_name', '')} {result.document.get('last_name', '')})")
                                    f.write(f" (Confidence: {result.get('confidence', 0):.2f})")

                                f.write("\n")

                                if len(category_results) > 3:
                                    f.write(f"... and {len(category_results) - 3} more results\n")

                                f.write("\n")

                            logger.info(f"Summary report generated: {output_path}")
                            return output_path