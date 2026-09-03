import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class TaskManager:
    """Central task manager to orchestrate OSINT modules"""

    def __init__(self):
        self.results = {}
        self.recursive_findings = {}

    async def execute(self, target_data: Dict[str, Any], modules: Dict[str, Any], recursive: bool = True) -> Dict[
        str, Any]:
        """Execute OSINT modules on target data"""
        logger.info(f"Executing {len(modules)} modules on {len(target_data)} targets")

        tasks = []
        for module_name, module in modules.items():
            task = asyncio.create_task(self._run_module(module_name, module, target_data))
            tasks.append(task)

        module_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = {}
        for i, (module_name, _) in enumerate(modules.items()):
            if isinstance(module_results[i], Exception):
                logger.error(f"Module {module_name} failed: {module_results[i]}")
                results[module_name] = {"error": str(module_results[i])}
            else:
                results[module_name] = module_results[i]

        if recursive:
            results = await self._process_recursive_findings(results, modules)

        return results

    async def _run_module(self, module_name: str, module: Any, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific module on target data"""
        logger.info(f"Running module: {module_name}")

        if module_name == 'identity':
            return await self._run_identity_module(module, target_data)
        elif module_name == 'migration':
            return await self._run_migration_module(module, target_data)
        elif module_name == 'social':
            return await self._run_social_module(module, target_data)
        elif module_name == 'network':
            return await self._run_network_module(module, target_data)
        elif module_name == 'darknet':
            return await self._run_darknet_module(module, target_data)
        else:
            logger.warning(f"Unknown module: {module_name}")
            return {"error": f"Unknown module: {module_name}"}

    async def _run_identity_module(self, module, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run identity module on target data"""
        results = {}

        if 'names' in target_data:
            name_results = []
            for name in target_data['names']:
                result = await module.search_name(name)
                name_results.append(result)
            results['names'] = name_results

        if 'passports' in target_data:
            passport_results = []
            for passport in target_data['passports']:
                result = await module.process_passport(passport)
                passport_results.append(result)
            results['passports'] = passport_results

        if 'snils' in target_data:
            snils_results = []
            for snils in target_data['snils']:
                result = await module.process_snils(snils)
                snils_results.append(result)
            results['snils'] = snils_results

        if 'licenses' in target_data:
            license_results = []
            for license_data in target_data['licenses']:
                result = await module.process_drivers_license(license_data)
                license_results.append(result)
            results['licenses'] = license_results

        return results

    async def _run_migration_module(self, module, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run migration module on target data"""
        results = {}

        if 'karta_polaka' in target_data:
            results['karta_polaka'] = await module.search_karta_polaka(target_data['karta_polaka'])

        if 'vnz_pmz' in target_data:
            results['vnz_pmz'] = await module.search_vnz_pmz(target_data['vnz_pmz'])

        if 'green_card' in target_data:
            results['green_card'] = await module.search_green_card(target_data['green_card'])

        return results

    async def _run_social_module(self, module, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run social module on target data"""
        results = {}

        if 'usernames' in target_data:
            username_results = []
            for username in target_data['usernames']:
                result = await module.search_username(username)
                username_results.append(result)
            results['usernames'] = username_results

        if 'names' in target_data:
            name_results = []
            for name in target_data['names']:
                result = await module.search_name(name)
                name_results.append(result)
            results['names'] = name_results

        return results

    async def _run_network_module(self, module, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run network module on target data"""
        results = {}

        if 'emails' in target_data:
            email_results = []
            for email in target_data['emails']:
                result = await module.search_email(email)
                email_results.append(result)
            results['emails'] = email_results

        if 'phones' in target_data:
            phone_results = []
            for phone in target_data['phones']:
                result = await module.search_phone(phone)
                phone_results.append(result)
            results['phones'] = phone_results

        if 'ips' in target_data:
            ip_results = []
            for ip in target_data['ips']:
                result = await module.search_ip(ip)
                ip_results.append(result)
            results['ips'] = ip_results

        if 'domains' in target_data:
            domain_results = []
            for domain in target_data['domains']:
                result = await module.search_domain(domain)
                domain_results.append(result)
            results['domains'] = domain_results

        return results

    async def _run_darknet_module(self, module, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run darknet module on target data"""
        results = {}

        for data_type, data_list in target_data.items():
            if isinstance(data_list, list) and data_list:
                type_results = []
                for item in data_list:
                    result = await module.search_darknet(item, data_type)
                    type_results.append(result)
                results[data_type] = type_results

        return results

    async def _process_recursive_findings(self, results: Dict[str, Any], modules: Dict[str, Any]) -> Dict[str, Any]:
        """Process findings from initial search for recursive analysis"""
        logger.info("Processing recursive findings")

        new_data = {}

        if 'identity' in results:
            for result_type in results['identity']:
                for result in results['identity'][result_type]:
                    if 'emails' in result:
                        if 'emails' not in new_data:
                            new_data['emails'] = []
                        new_data['emails'].extend(result['emails'])

        if 'social' in results:
            for result_type in results['social']:
                for result in results['social'][result_type]:
                    if 'phones' in result:
                        if 'phones' not in new_data:
                            new_data['phones'] = []
                        new_data['phones'].extend(result['phones'])

        if new_data:
            logger.info(f"Found {sum(len(v) for v in new_data.values())} new data points for recursive search")

            if 'emails' in new_data and 'network' in modules:
                email_results = []
                for email in new_data['emails']:
                    result = await modules['network'].search_email(email)
                    email_results.append(result)

                if 'network' not in results:
                    results['network'] = {}
                if 'recursive_emails' not in results['network']:
                    results['network']['recursive_emails'] = []
                results['network']['recursive_emails'] = email_results

            if 'phones' in new_data and 'network' in modules:
                phone_results = []
                for phone in new_data['phones']:
                    result = await modules['network'].search_phone(phone)
                    phone_results.append(result)

                if 'network' not in results:
                    results['network'] = {}
                if 'recursive_phones' not in results['network']:
                    results['network']['recursive_phones'] = []
                results['network']['recursive_phones'] = phone_results

            if 'network' in results:
                new_usernames = []
                for result_type in results['network']:
                    if isinstance(results['network'][result_type], list):
                        for result in results['network'][result_type]:
                            if 'usernames' in result:
                                new_usernames.extend(result['usernames'])

                if new_usernames and 'social' in modules:
                    username_results = []
                    for username in new_usernames:
                        result = await modules['social'].search_username(username)
                        username_results.append(result)

                    if 'social' not in results:
                        results['social'] = {}
                    if 'recursive_usernames' not in results['social']:
                        results['social']['recursive_usernames'] = []
                    results['social']['recursive_usernames'] = username_results

        return results