import json
import csv
import logging
from typing import Dict, List, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class DataHandler:
    """Handles data export and format conversion"""

    def __init__(self):
        self.supported_formats = ['json', 'csv', 'pdf']

    def save_as_json(self, data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """Save data as JSON"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Data saved as JSON to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
            return False

    def save_as_csv(self, data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """Save data as CSV"""
        try:
            flattened_data = self._flatten_data(data)

            if not flattened_data:
                logger.warning("No data to save as CSV")
                return False

            headers = set()
            for item in flattened_data:
                headers.update(item.keys())

            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(headers))
                writer.writeheader()
                writer.writerows(flattened_data)

            logger.info(f"Data saved as CSV to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
            return False

    def _flatten_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten nested data structure for CSV export"""
        flattened = []

        for module_name, module_data in data.items():
            if isinstance(module_data, dict):
                for data_type, type_data in module_data.items():
                    if isinstance(type_data, list):
                        for item in type_data:
                            if isinstance(item):
                                flat_item = {
                                    'module': module_name,
                                    'data_type': data_type
                                }

                                for key, value in item.items():
                                    if isinstance(value, dict):
                                        for sub_key, sub_value in value.items():
                                            flat_item[f"{key}_{sub_key}"] = sub_value
                                    elif isinstance(value, list):
                                        flat_item[key] = ", ".join(str(v) for v in value)
                                    else:
                                        flat_item[key] = value

                                flattened.append(flat_item)
                    elif isinstance(type_data, dict):
                        flat_item = {
                            'module': module_name,
                            'data_type': data_type
                        }

                        for key, value in type_data.items():
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    flat_item[f"{key}_{sub_key}"] = sub_value
                            elif isinstance(value, list):
                                flat_item[key] = ", ".join(str(v) for v in value)
                            else:
                                flat_item[key] = value

                        flattened.append(flat_item)

        return flattened