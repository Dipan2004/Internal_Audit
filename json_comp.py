import json
import re
import os
from datetime import datetime
from typing import Any, Dict, List, Union, Callable, Optional
import argparse

class FlexibleJSONConverter:
    """
    A completely flexible JSON converter that can transform any complex nested JSON 
    structure into simplified formats based on configurable rules loaded from config files.
    """
    
    def __init__(self, config_file: str = None):
        self.extraction_rules = {}
        self.value_extractors = {}
        self.aggregation_functions = {}
        self.output_template = {}
        self.global_config = {}
        
        # Register built-in extractors and aggregators
        self._register_builtin_functions()
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def _register_builtin_functions(self):
        """Register built-in extraction and aggregation functions."""
        # Built-in extractors
        self.value_extractors.update({
            "direct": self._extract_direct,
            "date_values": self._extract_date_values,
            "sum_all": self._extract_sum_all,
            "first_non_zero": self._extract_first_non_zero,
            "nested_sum": self._extract_nested_sum,
            "array_sum": self._extract_array_sum,
            "dict_values": self._extract_dict_values,
            "flatten_dict": self._extract_flatten_dict
        })
        
        # Built-in aggregators
        self.aggregation_functions.update({
            "sum": lambda values: sum(v for v in values if isinstance(v, (int, float))),
            "first": lambda values: values[0] if values else None,
            "last": lambda values: values[-1] if values else None,
            "average": lambda values: sum(v for v in values if isinstance(v, (int, float))) / len([v for v in values if isinstance(v, (int, float))]) if values else None,
            "max": lambda values: max(v for v in values if isinstance(v, (int, float))) if values else None,
            "min": lambda values: min(v for v in values if isinstance(v, (int, float))) if values else None,
            "concat": lambda values: " ".join(str(v) for v in values if v is not None),
            "merge_dicts": self._merge_dict_values
        })
    
    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = json.load(file)
            
            self.global_config = config.get("global_config", {})
            self.output_template = config.get("output_template", {})
            
            # Load extraction rules
            rules = config.get("extraction_rules", [])
            for rule in rules:
                self.add_extraction_rule(**rule)
            
            print(f"✅ Configuration loaded from {config_file}")
            print(f"   - {len(rules)} extraction rules loaded")
            print(f"   - Output template: {list(self.output_template.keys())}")
            
        except Exception as e:
            print(f"❌ Error loading config file {config_file}: {e}")
    
    def save_config(self, config_file: str):
        """Save current configuration to JSON file."""
        config = {
            "global_config": self.global_config,
            "output_template": self.output_template,
            "extraction_rules": [
                {
                    "rule_name": name,
                    **rule_config
                }
                for name, rule_config in self.extraction_rules.items()
            ]
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=2, ensure_ascii=False)
            print(f"✅ Configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving config file {config_file}: {e}")
    
    def add_extraction_rule(self, 
                          rule_name: str, 
                          paths: Union[str, List[str]], 
                          extractor: str = "direct",
                          aggregation: str = "first",
                          output_key: str = None,
                          note_number: str = None,
                          description: str = None,
                          conditions: Dict = None):
        """Add a flexible extraction rule."""
        self.extraction_rules[rule_name] = {
            "paths": paths if isinstance(paths, list) else [paths],
            "extractor": extractor,
            "aggregation": aggregation,
            "output_key": output_key or rule_name,
            "note_number": note_number,
            "description": description,
            "conditions": conditions or {}
        }
    
    def extract_by_path(self, data: Dict, path: str) -> Any:
        """Extract value from JSON using flexible path notation."""
        # Handle different path separators
        path = path.replace('/', '.').replace('->', '.')
        
        # Handle wildcards and patterns
        if '*' in path or '**' in path:
            return self._extract_wildcard_paths(data, path)
        
        # Handle array notation [0], [*], etc.
        if '[' in path and ']' in path:
            return self._extract_array_paths(data, path)
        
        # Standard dot notation
        keys = [k for k in path.split('.') if k]
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                current = current[idx] if 0 <= idx < len(current) else None
            else:
                return None
                
            if current is None:
                return None
        
        return current
    
    def _extract_wildcard_paths(self, data: Dict, pattern: str) -> List[Any]:
        """Extract all values matching wildcard pattern."""
        results = []
        
        def traverse(obj, path_parts, current_path=""):
            if not path_parts:
                results.append(obj)
                return
            
            part = path_parts[0]
            remaining = path_parts[1:]
            
            if part == "*":
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        traverse(value, remaining, f"{current_path}.{key}" if current_path else key)
                elif isinstance(obj, list):
                    for i, value in enumerate(obj):
                        traverse(value, remaining, f"{current_path}[{i}]")
            elif part == "**":
                # Deep wildcard - traverse all levels
                traverse(obj, remaining, current_path)  # Try current level
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        traverse(value, path_parts, f"{current_path}.{key}" if current_path else key)
                elif isinstance(obj, list):
                    for i, value in enumerate(obj):
                        traverse(value, path_parts, f"{current_path}[{i}]")
            else:
                if isinstance(obj, dict) and part in obj:
                    traverse(obj[part], remaining, f"{current_path}.{part}" if current_path else part)
        
        path_parts = pattern.split('.')
        traverse(data, path_parts)
        return results
    
    def _extract_array_paths(self, data: Dict, path: str) -> Any:
        """Handle array notation in paths."""
        # Split path into segments
        segments = []
        current_segment = ""
        in_bracket = False
        
        for char in path:
            if char == '[':
                if current_segment:
                    segments.append(current_segment)
                    current_segment = ""
                in_bracket = True
            elif char == ']':
                if in_bracket:
                    segments.append(f"[{current_segment}]")
                    current_segment = ""
                    in_bracket = False
            elif char == '.' and not in_bracket:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = ""
            else:
                current_segment += char
        
        if current_segment:
            segments.append(current_segment)
        
        # Navigate through segments
        current = data
        for segment in segments:
            if segment.startswith('[') and segment.endswith(']'):
                # Array index or wildcard
                index_str = segment[1:-1]
                if index_str == '*':
                    # Collect all array elements
                    if isinstance(current, list):
                        return current
                elif index_str.isdigit():
                    # Specific index
                    idx = int(index_str)
                    if isinstance(current, list) and 0 <= idx < len(current):
                        current = current[idx]
                    else:
                        return None
            else:
                # Regular key
                if isinstance(current, dict):
                    current = current.get(segment)
                else:
                    return None
            
            if current is None:
                return None
        
        return current
    
    # Built-in extractor functions
    def _extract_direct(self, data: Any) -> Any:
        """Extract data as-is."""
        return data
    
    def _extract_date_values(self, data: Any) -> Dict[str, Any]:
        """Extract values with date-based keys."""
        if not isinstance(data, dict):
            return {"value": data} if data is not None else {}
        
        date_values = {}
        for key, value in data.items():
            # Look for date patterns
            year_match = re.search(r'(\d{4})', str(key))
            if year_match:
                year = year_match.group(1)
                date_values[f"value_{year}"] = value
            elif str(key).lower() in ['current', 'previous', 'latest']:
                date_values[f"value_{key.lower()}"] = value
        
        # If no date patterns found, return the original data
        return date_values if date_values else {"value": data}
    
    def _extract_sum_all(self, data: Any) -> float:
        """Sum all numeric values in nested structure."""
        total = 0
        
        def add_numbers(obj):
            nonlocal total
            if isinstance(obj, (int, float)):
                total += obj
            elif isinstance(obj, dict):
                for value in obj.values():
                    if str(value).replace('.', '').replace('-', '').isdigit():
                        try:
                            total += float(value)
                        except:
                            pass
                    else:
                        add_numbers(value)
            elif isinstance(obj, list):
                for item in obj:
                    add_numbers(item)
        
        add_numbers(data)
        return total
    
    def _extract_first_non_zero(self, data: Any) -> Any:
        """Extract first non-zero value."""
        def find_first_non_zero(obj):
            if isinstance(obj, (int, float)) and obj != 0:
                return obj
            elif isinstance(obj, dict):
                for value in obj.values():
                    result = find_first_non_zero(value)
                    if result is not None:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_first_non_zero(item)
                    if result is not None:
                        return result
            return None
        
        return find_first_non_zero(data)
    
    def _extract_nested_sum(self, data: Any) -> float:
        """Sum values from nested dictionaries, ignoring metadata."""
        total = 0
        
        def sum_nested(obj, path=""):
            nonlocal total
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Skip metadata keys
                    if key.startswith('_') or 'metadata' in key.lower():
                        continue
                    
                    if isinstance(value, (int, float)):
                        total += value
                    else:
                        sum_nested(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (int, float)):
                        total += item
                    else:
                        sum_nested(item, f"{path}[{i}]")
        
        sum_nested(data)
        return total
    
    def _extract_array_sum(self, data: Any) -> float:
        """Sum numeric values from arrays."""
        if isinstance(data, list):
            return sum(item for item in data if isinstance(item, (int, float)))
        return 0
    
    def _extract_dict_values(self, data: Any) -> List[Any]:
        """Extract all values from dictionary."""
        if isinstance(data, dict):
            return list(data.values())
        return [data] if data is not None else []
    
    def _extract_flatten_dict(self, data: Any) -> Dict[str, Any]:
        """Flatten nested dictionary."""
        result = {}
        
        def flatten(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, dict):
                        flatten(value, new_key)
                    else:
                        result[new_key] = value
        
        flatten(data)
        return result
    
    def _merge_dict_values(self, values: List[Any]) -> Dict[str, Any]:
        """Merge multiple dictionaries."""
        merged = {}
        for value in values:
            if isinstance(value, dict):
                merged.update(value)
        return merged
    
    def apply_extractor(self, data: Any, extractor_type: str) -> Any:
        """Apply the specified extractor to the data."""
        if extractor_type in self.value_extractors:
            return self.value_extractors[extractor_type](data)
        else:
            print(f"⚠️  Unknown extractor '{extractor_type}', using 'direct'")
            return data
    
    def apply_aggregation(self, values: List[Any], aggregation_type: str) -> Any:
        """Apply aggregation function to values."""
        if not values:
            return None
        
        # Filter out None values
        filtered_values = [v for v in values if v is not None]
        
        if aggregation_type in self.aggregation_functions:
            return self.aggregation_functions[aggregation_type](filtered_values)
        else:
            print(f"⚠️  Unknown aggregation '{aggregation_type}', using 'first'")
            return filtered_values[0] if filtered_values else None
    
    def convert(self, input_data: Union[str, Dict], input_file: str = None) -> Dict:
        """Convert complex JSON to simplified format using configured rules."""
        # Parse input if it's a string
        if isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            data = input_data
        
        print(f"🔄 Converting data using {len(self.extraction_rules)} rules...")
        
        # Initialize output with template
        output = dict(self.output_template)
        extracted_items = []
        
        # Process each extraction rule
        for rule_name, rule_config in self.extraction_rules.items():
            print(f"   Processing rule: {rule_name}")
            
            extracted_values = []
            
            # Extract data for each path in the rule
            for path in rule_config["paths"]:
                try:
                    raw_data = self.extract_by_path(data, path)
                    if raw_data is not None:
                        processed_data = self.apply_extractor(raw_data, rule_config["extractor"])
                        if processed_data is not None:
                            extracted_values.append(processed_data)
                except Exception as e:
                    print(f"     ⚠️  Error processing path '{path}': {e}")
                    continue
            
            # Apply aggregation
            if extracted_values:
                try:
                    final_value = self.apply_aggregation(extracted_values, rule_config["aggregation"])
                    
                    if final_value is not None:
                        # Create output item
                        item = {
                            "name": rule_config["output_key"],
                        }
                        
                        # Handle different value types
                        if isinstance(final_value, dict):
                            item.update(final_value)
                        else:
                            item["value"] = final_value
                        
                        # Add optional fields
                        if rule_config.get("note_number"):
                            item["note"] = rule_config["note_number"]
                        if rule_config.get("description"):
                            item["description"] = rule_config["description"]
                        
                        extracted_items.append(item)
                        print(f"     ✅ Extracted: {rule_config['output_key']}")
                    else:
                        print(f"     ⚠️  No valid data found for: {rule_name}")
                        
                except Exception as e:
                    print(f"     ❌ Error aggregating data for '{rule_name}': {e}")
            else:
                print(f"     ⚠️  No data extracted for: {rule_name}")
        
        # Update output structure
        if "extraction_info" in output:
            output["extraction_info"]["total_items_extracted"] = len(extracted_items)
            output["extraction_info"]["extraction_timestamp"] = datetime.now().isoformat()
            if input_file:
                output["extraction_info"]["source_file"] = input_file
        
        # Add extracted data to appropriate section
        data_key = self.global_config.get("data_key", "data")
        if data_key in output:
            output[data_key] = extracted_items
        else:
            output["extracted_data"] = extracted_items
        
        print(f"✅ Conversion complete! {len(extracted_items)} items extracted.")
        return output

def create_sample_config():
    """Create a sample configuration file for financial data."""
    config = {
        "global_config": {
            "description": "Financial data extraction configuration",
            "version": "1.0",
            "data_key": "balance_sheet_data"
        },
        "output_template": {
            "extraction_info": {
                "total_items_extracted": 0,
                "extraction_timestamp": "",
                "source_file": "",
                "config_version": "1.0"
            },
            "balance_sheet_data": []
        },
        "extraction_rules": [
            {
                "rule_name": "Share Capital",
                "paths": [
                    "company_financial_data.share_capital.Total issued, subscribed and fully paid-up share capital",
                    "*.share_capital.*",
                    "**.share_capital"
                ],
                "extractor": "date_values",
                "aggregation": "first",
                "output_key": "Share Capital",
                "note_number": "2",
                "description": "Total issued and paid-up share capital"
            },
            {
                "rule_name": "Reserves and Surplus",
                "paths": [
                    "company_financial_data.reserves_and_surplus.Balance, at the end of the year",
                    "*.reserves_and_surplus.*end*",
                    "**.reserves**balance"
                ],
                "extractor": "date_values",
                "aggregation": "first",
                "output_key": "Reserves and Surplus",
                "note_number": "3",
                "description": "Accumulated reserves and surplus"
            },
            {
                "rule_name": "Trade Receivables",
                "paths": [
                    "company_financial_data.current_assets.*.Trade receivables.*",
                    "**.trade*receivables**",
                    "**.receivables**"
                ],
                "extractor": "nested_sum",
                "aggregation": "sum",
                "output_key": "Trade Receivables",
                "note_number": "12",
                "description": "Total trade receivables"
            },
            {
                "rule_name": "Cash and Bank Balances",
                "paths": [
                    "company_financial_data.current_assets.*.Cash and bank balances.*",
                    "**.cash**",
                    "**.bank**balances"
                ],
                "extractor": "nested_sum",
                "aggregation": "sum",
                "output_key": "Cash and Bank Balances",
                "note_number": "13",
                "description": "Total cash and bank balances"
            },
            {
                "rule_name": "Fixed Assets",
                "paths": [
                    "company_financial_data.fixed_assets.**.net_carrying_value.closing",
                    "**.fixed_assets**",
                    "**.tangible_assets**",
                    "**.intangible_assets**"
                ],
                "extractor": "sum_all",
                "aggregation": "sum",
                "output_key": "Fixed Assets",
                "note_number": "9",
                "description": "Total fixed assets net value"
            }
        ]
    }
    
    return config

def auto_generate_config(sample_data: Dict, output_file: str = "auto_config.json"):
    """Auto-generate configuration based on sample data structure."""
    print("🤖 Auto-generating configuration from sample data...")
    
    def find_numeric_paths(data, path="", max_depth=5):
        """Find paths to numeric values."""
        if max_depth <= 0:
            return []
        
        paths = []
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, (int, float)):
                    paths.append(new_path)
                elif isinstance(value, (dict, list)):
                    paths.extend(find_numeric_paths(value, new_path, max_depth - 1))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (int, float)):
                    paths.append(f"{path}[{i}]")
                elif isinstance(item, (dict, list)):
                    paths.extend(find_numeric_paths(item, f"{path}[{i}]", max_depth - 1))
        
        return paths
    
    # Find all numeric paths
    numeric_paths = find_numeric_paths(sample_data)
    
    # Group similar paths
    path_groups = {}
    for path in numeric_paths:
        # Extract meaningful keywords
        keywords = re.findall(r'[a-zA-Z_]+', path.lower())
        key_words = [w for w in keywords if len(w) > 2 and w not in ['the', 'and', 'for', 'with']]
        
        if key_words:
            group_key = "_".join(key_words[:2])  # Use first 2 keywords
            if group_key not in path_groups:
                path_groups[group_key] = []
            path_groups[group_key].append(path)
    
    # Generate rules
    rules = []
    for group_name, paths in path_groups.items():
        rules.append({
            "rule_name": group_name.replace('_', ' ').title(),
            "paths": paths[:3],  # Limit to 3 paths per rule
            "extractor": "date_values" if any("date" in p or "202" in p for p in paths) else "direct",
            "aggregation": "sum" if len(paths) > 1 else "first",
            "output_key": group_name.replace('_', ' ').title(),
            "description": f"Auto-generated rule for {group_name}"
        })
    
    config = {
        "global_config": {
            "description": "Auto-generated configuration",
            "version": "1.0",
            "data_key": "extracted_data"
        },
        "output_template": {
            "extraction_info": {
                "total_items_extracted": 0,
                "extraction_timestamp": "",
                "source_file": "",
                "generation_method": "auto"
            },
            "extracted_data": []
        },
        "extraction_rules": rules
    }
    
    # Save config
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Auto-generated config saved to {output_file}")
    print(f"   Found {len(rules)} extraction rules")
    return config

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Flexible JSON Converter")
    parser.add_argument("input_file", help="Input JSON file to convert")
    parser.add_argument("-c", "--config", help="Configuration file", 
                       default="extraction_config.json")
    parser.add_argument("-o", "--output", help="Output file", 
                       default="converted_output.json")
    parser.add_argument("--auto-config", action="store_true", 
                       help="Auto-generate configuration from input")
    parser.add_argument("--sample-config", action="store_true",
                       help="Create sample configuration file")
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.sample_config:
        config = create_sample_config()
        with open("sample_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ Sample configuration created: sample_config.json")
        return
    
    # Load input data
    if not os.path.exists(args.input_file):
        print(f"❌ Input file not found: {args.input_file}")
        return
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        print(f"✅ Loaded input file: {args.input_file}")
    except Exception as e:
        print(f"❌ Error loading input file: {e}")
        return
    
    # Auto-generate config if requested
    if args.auto_config:
        auto_generate_config(input_data, args.config)
    
    # Create converter and process
    converter = FlexibleJSONConverter(args.config)
    
    if not converter.extraction_rules:
        print("⚠️  No extraction rules loaded. Use --sample-config to create a template.")
        return
    
    # Convert data
    result = converter.convert(input_data, args.input_file)
    
    # Save output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Output saved to: {args.output}")
    except Exception as e:
        print(f"❌ Error saving output: {e}")

# Convenience function for direct usage
def convert_json_file(input_file: str, 
                     config_file: str = None, 
                     output_file: str = None):
    """Convenience function to convert a JSON file."""
    
    # Set default paths
    if not config_file:
        config_file = "extraction_config.json"
    if not output_file:
        output_file = input_file.replace('.json', '_converted.json')
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return None
    
    # Load input data
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading {input_file}: {e}")
        return None
    
    # Create config if it doesn't exist
    if not os.path.exists(config_file):
        print(f"⚠️  Config file not found. Creating sample config: {config_file}")
        config = create_sample_config()
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Create converter and convert
    converter = FlexibleJSONConverter(config_file)
    result = converter.convert(input_data, input_file)
    
    # Save result
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Converted data saved to: {output_file}")
        return result
    except Exception as e:
        print(f"❌ Error saving output: {e}")
        return None

if __name__ == "__main__":
    # If run directly, check for command line arguments
    import sys
    
    if len(sys.argv) > 1:
        main()
    else:
        # Default behavior - process complete_financial_mapping.json
        input_file = "complete_financial_mapping.json"
        
        print("🚀 Flexible JSON Converter")
        print("=" * 50)
        
        if os.path.exists(input_file):
            print(f"📁 Processing: {input_file}")
            result = convert_json_file(
                input_file,
                config_file="financial_extraction_config.json",
                output_file="output/simplified_financial_data.json"
            )
            
            if result:
                print("🎉 Conversion completed successfully!")
        else:
            print(f"❌ Default input file not found: {input_file}")
            print("\nUsage options:")
            print("1. Place your JSON file at: output/complete_financial_mapping.json")
            print("2. Use command line: python script.py your_file.json")
            print("3. Create sample config: python script.py --sample-config")