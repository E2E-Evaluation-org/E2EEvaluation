"""
Utility file for the common json export
"""

import json

from utilities.yaml_export import CEC_Export, Inter_CEC_Export


def _json_default(value):
    """Convert objects for storing in json format."""
    if hasattr(value, "__dict__"):
        return value.__dict__
    return str(value)


def export_to_json(output_path, cause_effect_chains):
    """Save cause-effect chains and their underlying tasks as JSON at the passed output_path, using CEC_Export and Inter_CEC_Export from utilities.yaml_export."""
    if isinstance(cause_effect_chains[0], tuple):
        obj = Inter_CEC_Export(cause_effect_chains)
    else:
        obj = CEC_Export(cause_effect_chains)

    filename = f'{output_path}cause_effect_chains.json'
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(obj.__dict__, json_file, default=_json_default, indent=2)

    return filename
