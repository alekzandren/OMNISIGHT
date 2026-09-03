#!/usr/bin/env python3

import asyncio
import click
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.task_manager import TaskManager
from core.data_handler import DataHandler
from reports.generator import ReportGenerator
from modules.identity_processor import IdentityProcessor
from modules.migration_checker import MigrationChecker
from modules.social_scraper import SocialScraper
from modules.network_analyzer import NetworkAnalyzer
from modules.darknet_interface import DarknetInterface

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('omnisight.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """OmniSight: Advanced OSINT Framework"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--input', '-i', required=True, help='Input file with target data')
@click.option('--output', '-o', default='reports', help='Output directory for reports')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'csv', 'pdf']), help='Output format')
@click.option('--modules', '-m', multiple=True, help='Specific modules to run')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Enable recursive searching')
@click.pass_context
def scan(ctx, input, output, format, modules, recursive):
    """Run OSINT scan on target data"""
    logger.info(f"Starting OmniSight scan with input: {input}")

    Path(output).mkdir(exist_ok=True)

    task_manager = TaskManager()
    data_handler = DataHandler()

    try:
        with open(input, 'r') as f:
            target_data = json.load(f)
        logger.info(f"Loaded target data: {len(target_data)} entries")
    except Exception as e:
        logger.error(f"Failed to load input data: {e}")
        return

    all_modules = {
        'identity': IdentityProcessor(),
        'migration': MigrationChecker(),
        'social': SocialScraper(),
        'network': NetworkAnalyzer(),
        'darknet': DarknetInterface()
    }

    if modules:
        selected_modules = {k: v for k, v in all_modules.items() if k in modules}
    else:
        selected_modules = all_modules

    async def run_scan():
        results = await task_manager.execute(target_data, selected_modules, recursive)

        output_path = Path(output) / f"omnisight_results.{format}"
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif format == 'csv':
            data_handler.save_as_csv(results, output_path)
        elif format == 'pdf':
            report_gen = ReportGenerator()
            report_gen.generate_pdf(results, output_path)

        logger.info(f"Results saved to {output_path}")
        return results

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_scan())

    click.echo(f"\nScan completed. Found {len(results)} entries.")
    for module_name, module_results in results.items():
        click.echo(f"  {module_name}: {len(module_results)} results")


@cli.command()
@click.option('--target', '-t', required=True, help='Target to search for')
@click.option('--type', '-tp', required=True, type=click.Choice(['email', 'phone', 'username', 'name']),
              help='Target type')
@click.option('--output', '-o', default='quick_scan.json', help='Output file')
@click.pass_context
def quick(ctx, target, type, output):
    """Quick scan for a single target"""
    logger.info(f"Quick scan for {type}: {target}")

    if type == 'email':
        module = NetworkAnalyzer()
        method = 'search_email'
    elif type == 'phone':
        module = NetworkAnalyzer()
        method = 'search_phone'
    elif type == 'username':
        module = SocialScraper()
        method = 'search_username'
    elif type == 'name':
        module = IdentityProcessor()
        method = 'search_name'

    async def run_quick_scan():
        result = await getattr(module, method)(target)

        with open(output, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        logger.info(f"Results saved to {output}")
        return result

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_quick_scan())

    click.echo(f"\nFound {len(results)} results for {target}:")
    for result in results:
        click.echo(f"  - {result}")


if __name__ == '__main__':
    cli()