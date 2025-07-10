import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import time




class TrialBalanceNotesGenerator:
    def __init__(self, config_file: str = "config.json", api_endpoint: str = None, api_key: str = None):
        """
        Initialize the generator with configuration
        
        Args:
            config_file: Path to configuration JSON file
            api_endpoint: Override API endpoint
            api_key: Override API key
        """
        self.config = self.load_config(config_file)
        
        # Override config with direct parameters if provided
        if api_endpoint:
            self.config['api']['endpoint'] = api_endpoint
        if api_key:
            self.config['api']['key'] = api_key
        
        self.api_endpoint = self.config.get('api', {}).get('endpoint')
        self.api_key = self.config.get('api', {}).get('key')
        
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "api": {
                "endpoint": None,
                "key": None,
                "model": "deepseek-chat",
                "temperature": 0.1,
                "max_tokens": 3000,
                "timeout": 30
            },
            "schedule_iii_mapping": {
                "security deposits": "10",
                "long term": "10",
                "advances": "10",
                "deposits": "10",
                "consumables": "11",
                "inventory": "11",
                "raw materials": "11",
                "finished goods": "11",
                "work in progress": "11",
                "stores": "11",
                "cash": "12",
                "bank": "12",
                "trade receivables": "13",
                "debtors": "13",
                "short term loans": "14",
                "short term advances": "14",
                "other current assets": "15",
                "prepaid expenses": "15",
                "trade payables": "16",
                "creditors": "16",
                "other current liabilities": "17",
                "provisions": "18",
                "employee benefits": "18"
            },
            "note_titles": {
                "10": "Long Term Loans and Advances",
                "11": "Inventories",
                "12": "Cash and Bank Balances",
                "13": "Trade Receivables",
                "14": "Short-term Loans and Advances",
                "15": "Other Current Assets",
                "16": "Trade Payables",
                "17": "Other Current Liabilities",
                "18": "Provisions"
            },
            "formatting": {
                "currency_symbol": "₹",
                "amount_unit": "lakhs",
                "decimal_places": 2,
                "date_format": "%Y-%m-%d",
                "conversion_factor": 100000
            },
            "validation": {
                "required_fields": ["account_name", "amount", "date"],
                "required_note_fields": ["title", "full_title", "structure", "metadata"]
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge user config with default config
                    self.merge_configs(default_config, user_config)
            except Exception as e:
                print(f"⚠️  Error loading config file: {e}. Using default configuration.")
        else:
            print(f"ℹ️  Config file {config_file} not found. Creating default config.")
            self.save_config(default_config, config_file)
        
        return default_config
    
    def merge_configs(self, default: Dict, user: Dict) -> None:
        """
        Recursively merge user config into default config
        
        Args:
            default: Default configuration
            user: User configuration
        """
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self.merge_configs(default[key], value)
            else:
                default[key] = value
    
    def save_config(self, config: Dict[str, Any], config_file: str) -> None:
        """
        Save configuration to JSON file
        
        Args:
            config: Configuration dictionary
            config_file: Path to save configuration
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Default configuration saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def categorize_account(self, account_name: str) -> str:
        """
        Categorize account based on name to Schedule III note number
        
        Args:
            account_name: Name of the account
            
        Returns:
            Schedule III note number
        """
        account_lower = account_name.lower()
        mapping = self.config['schedule_iii_mapping']
        
        for keyword, note_num in mapping.items():
            if keyword in account_lower:
                return note_num
        
        # Default to other current assets if no match found
        return "15"
    
    def format_amount(self, amount: float) -> str:
        """
        Format amount according to configuration
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted amount string
        """
        formatting = self.config['formatting']
        conversion_factor = formatting['conversion_factor']
        decimal_places = formatting['decimal_places']
        
        converted_amount = amount / conversion_factor
        return f"{converted_amount:.{decimal_places}f}"
    
    def build_internal_prompt(self, tb_data: List[Dict]) -> str:
        """
        Build the internal prompt to send to the LLM
        
        Args:
            tb_data: List of trial balance entries
            
        Returns:
            Formatted prompt string
        """
        # Get configuration values
        currency_symbol = self.config['formatting']['currency_symbol']
        amount_unit = self.config['formatting']['amount_unit']
        note_titles = self.config['note_titles']
        
        # Group data by account and date for better presentation
        account_groups = {}
        for entry in tb_data:
            account_name = entry['account_name']
            if account_name not in account_groups:
                account_groups[account_name] = []
            account_groups[account_name].append(entry)
        
        # Format the trial balance data for the prompt
        formatted_data = []
        for account_name, entries in account_groups.items():
            formatted_data.append(f"\n{account_name}:")
            for entry in sorted(entries, key=lambda x: x['date'], reverse=True):
                formatted_data.append(f"  • {entry['date']}: {currency_symbol}{entry['amount']:,.2f}")
        
        tb_summary = "\n".join(formatted_data)
        
        # Build note examples from configuration
        note_examples = []
        for note_num, title in note_titles.items():
            note_examples.append(f"   - Note {note_num}: {title}")
        
        note_examples_str = "\n".join(note_examples)
        
        # Get current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        internal_prompt = f"""You are an expert chartered accountant specializing in Indian accounting standards and Schedule III compliance under the Companies Act, 2013.

TASK: Generate "Notes to Accounts" in Schedule III format based on the provided Trial Balance data.

TRIAL BALANCE DATA:
{tb_summary}

CONTEXT:
- All amounts are in Indian Rupees ({currency_symbol})
- Data contains entries for financial years ending March 31, 2024 and March 31, 2023
- Follow Schedule III format under Companies Act, 2013
- Create comparative financial statements
- Present amounts in {amount_unit}

AVAILABLE SCHEDULE III NOTES:
{note_examples_str}

INSTRUCTIONS:
1. Analyze the account names and amounts to identify which Schedule III note categories they belong to
2. Group similar accounts under appropriate note numbers based on the available notes above
3. Structure the data with proper categorization and subcategorization
4. Include comparative figures for both years where available
5. Convert amounts to {amount_unit} (divide by {self.config['formatting']['conversion_factor']:,}) for presentation
6. Calculate totals and subtotals appropriately
7. Follow Schedule III format strictly

OUTPUT FORMAT REQUIREMENTS:
Return ONLY a valid JSON object in this exact structure (no additional text):

{{
  "note_number": {{
    "title": "Note Title",
    "full_title": "Note Number. Full Title",
    "structure": [
      {{
        "category": "In {amount_unit.title()}" or "Category Name",
        "subcategories": [
          {{
            "label": "March 31, 2024" or "Account Description",
            "value": "amount_in_{amount_unit}",
            "previous_value": "previous_year_amount (optional)"
          }}
        ],
        "total": "total_amount_in_{amount_unit} (if applicable)",
        "previous_total": "previous_year_total (if applicable)"
      }}
    ],
    "metadata": {{
      "note_number": "note_number",
      "generated_on": "{current_time}"
    }}
  }}
}}

SPECIFIC FORMATTING RULES:
- Convert all amounts to {amount_unit} ({currency_symbol}1,000,000 = {self.format_amount(1000000)} {amount_unit})
- Show amounts with {self.config['formatting']['decimal_places']} decimal places
- Always include comparative year headers where both years have data
- For accounts with both years, show current year and previous year values
- Calculate accurate totals for each category
- Use proper Schedule III terminology and structure

VALIDATION RULES:
- Only create notes for accounts that actually exist in the trial balance
- Do not hallucinate or create fictional account entries
- Ensure all amounts are mathematically consistent
- Group accounts logically under appropriate Schedule III categories
- Maintain consistency in formatting and structure

Begin analysis and generate the structured JSON output:"""

        return internal_prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        Send prompt to LLM and get response
        
        Args:
            prompt: The formatted prompt to send
            
        Returns:
            Raw response from LLM
        """
        if not self.api_endpoint:
            # Return mock response for testing
            return self.generate_mock_response()
        
        api_config = self.config['api']
        payload = {
            "model": api_config['model'],
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert chartered accountant. Respond only with valid JSON in the exact format requested."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": api_config['temperature'],
            "max_tokens": api_config['max_tokens']
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                headers=self.headers,
                json=payload,
                timeout=api_config['timeout']
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def generate_mock_response(self) -> str:
        """
        Generate a mock response for testing without actual LLM call
        
        Returns:
            Mock JSON response
        """
        # Generate mock response based on configuration
        note_titles = self.config['note_titles']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        mock_response = {
            "10": {
                "title": note_titles.get("10", "Long Term Loans and Advances"),
                "full_title": f"10. {note_titles.get('10', 'Long Term Loans and Advances')}",
                "structure": [
                    {
                        "category": f"In {self.config['formatting']['amount_unit'].title()}",
                        "subcategories": [
                            {"label": "March 31, 2024", "value": "10.00"},
                            {"label": "March 31, 2023", "value": "8.50"}
                        ]
                    },
                    {
                        "category": "Unsecured, considered good",
                        "subcategories": [
                            {
                                "label": "Long Term - Security Deposits",
                                "value": "10.00",
                                "previous_value": "8.50"
                            }
                        ],
                        "total": "10.00",
                        "previous_total": "8.50"
                    }
                ],
                "metadata": {
                    "note_number": "10",
                    "generated_on": current_time
                }
            },
            "11": {
                "title": note_titles.get("11", "Inventories"),
                "full_title": f"11. {note_titles.get('11', 'Inventories')}",
                "structure": [
                    {
                        "category": f"In {self.config['formatting']['amount_unit'].title()}",
                        "subcategories": [
                            {"label": "March 31, 2024", "value": "3.00"},
                            {"label": "March 31, 2023", "value": "2.80"}
                        ]
                    },
                    {
                        "category": "Consumables",
                        "subcategories": [],
                        "total": "3.00",
                        "previous_total": "2.80"
                    }
                ],
                "metadata": {
                    "note_number": "11",
                    "generated_on": current_time
                }
            }
        }
        
        return json.dumps(mock_response, indent=2)
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate LLM response
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Parsed JSON object
        """
        try:
            # Clean the response - remove any markdown formatting or extra text
            response = response.strip()
            
            # Try to extract JSON from response if it's wrapped in text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response
            
            # Remove any potential markdown code blocks
            json_str = re.sub(r'```json\s*', '', json_str)
            json_str = re.sub(r'```\s*$', '', json_str)
            
            # Parse JSON
            parsed_response = json.loads(json_str)
            
            # Validate structure
            if not isinstance(parsed_response, dict):
                raise ValueError("Response must be a JSON object")
            
            # Validate each note has required structure
            required_fields = self.config['validation']['required_note_fields']
            for note_num, note_data in parsed_response.items():
                if not isinstance(note_data, dict):
                    raise ValueError(f"Note {note_num} must be an object")
                
                for field in required_fields:
                    if field not in note_data:
                        raise ValueError(f"Note {note_num} missing required field: {field}")
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing response: {str(e)}")
    
    def validate_input_data(self, tb_data: List[Dict]) -> List[Dict]:
        """
        Validate input trial balance data
        
        Args:
            tb_data: List of trial balance entries
            
        Returns:
            Validated and cleaned data
        """
        required_fields = self.config['validation']['required_fields']
        validated_data = []
        
        for i, entry in enumerate(tb_data):
            # Check required fields
            for field in required_fields:
                if field not in entry:
                    raise ValueError(f"Entry {i} missing required field: {field}")
            
            # Validate amount is numeric
            if not isinstance(entry['amount'], (int, float)):
                try:
                    entry['amount'] = float(entry['amount'])
                except ValueError:
                    raise ValueError(f"Entry {i} has invalid amount: {entry['amount']}")
            
            # Validate date format
            try:
                datetime.strptime(entry['date'], '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"Entry {i} has invalid date format: {entry['date']}. Expected YYYY-MM-DD")
            
            validated_data.append(entry)
        
        return validated_data
    
    def post_process_response(self, parsed_response: Dict[str, Any], tb_data: List[Dict]) -> Dict[str, Any]:
        """
        Post-process and validate the parsed response
        
        Args:
            parsed_response: Parsed JSON from LLM
            tb_data: Original trial balance data for validation
            
        Returns:
            Cleaned and validated response
        """
        # Create a lookup for actual amounts from TB data
        tb_lookup = {}
        for entry in tb_data:
            key = f"{entry['account_name']}_{entry['date']}"
            tb_lookup[key] = entry['amount']
        
        # Validate and clean the response
        cleaned_response = {}
        
        for note_num, note_data in parsed_response.items():
            if isinstance(note_data, dict) and 'structure' in note_data:
                cleaned_note = {
                    'title': note_data.get('title', ''),
                    'full_title': note_data.get('full_title', ''),
                    'structure': [],
                    'metadata': note_data.get('metadata', {})
                }
                
                # Ensure metadata has required fields
                if 'note_number' not in cleaned_note['metadata']:
                    cleaned_note['metadata']['note_number'] = note_num
                if 'generated_on' not in cleaned_note['metadata']:
                    cleaned_note['metadata']['generated_on'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Process each category in the structure
                for category in note_data.get('structure', []):
                    cleaned_category = {
                        'category': category.get('category', ''),
                        'subcategories': []
                    }
                    
                    # Process subcategories
                    for subcat in category.get('subcategories', []):
                        cleaned_subcat = {
                            'label': subcat.get('label', ''),
                            'value': subcat.get('value', ''),
                        }
                        if 'previous_value' in subcat:
                            cleaned_subcat['previous_value'] = subcat['previous_value']
                        
                        cleaned_category['subcategories'].append(cleaned_subcat)
                    
                    # Add totals if present
                    if 'total' in category:
                        cleaned_category['total'] = category['total']
                    if 'previous_total' in category:
                        cleaned_category['previous_total'] = category['previous_total']
                    
                    cleaned_note['structure'].append(cleaned_category)
                
                cleaned_response[note_num] = cleaned_note
        
        return cleaned_response
    
    def generate_notes(self, tb_data: List[Dict]) -> Dict[str, Any]:
        """
        Main method to generate Schedule III notes from trial balance data
        
        Args:
            tb_data: List of trial balance entries
            
        Returns:
            Structured notes in Schedule III format
        """
        try:
            print("Step 1: Validating input data...")
            # Step 1: Validate input data
            validated_data = self.validate_input_data(tb_data)
            
            print("Step 2: Building internal prompt...")
            # Step 2: Build internal prompt
            prompt = self.build_internal_prompt(validated_data)
            
            print("Step 3: Calling LLM...")
            # Step 3: Call LLM
            llm_response = self.call_llm(prompt)
            
            print("Step 4: Parsing LLM response...")
            # Step 4: Parse response
            parsed_response = self.parse_llm_response(llm_response)
            
            print("Step 5: Post-processing...")
            # Step 5: Post-process
            final_response = self.post_process_response(parsed_response, validated_data)
            
            print("✅ Notes generated successfully!")
            return final_response
            
        except Exception as e:
            raise Exception(f"Error generating notes: {str(e)}")
    
    def save_notes_to_file(self, notes: Dict[str, Any], filename: str = "schedule_iii_notes.json"):
        """
        Save generated notes to JSON file
        
        Args:
            notes: Generated notes dictionary
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            print(f"✅ Notes saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving notes: {str(e)}")
    
    def print_notes_summary(self, notes: Dict[str, Any]):
        """
        Print a summary of generated notes
        
        Args:
            notes: Generated notes dictionary
        """
        print("\n" + "="*60)
        print("📊 SCHEDULE III NOTES SUMMARY")
        print("="*60)
        
        for note_num, note_data in notes.items():
            print(f"\n{note_data['full_title']}")
            print("-" * len(note_data['full_title']))
            
            for category in note_data['structure']:
                if category['category']:
                    print(f"  📂 {category['category']}")
                
                for subcat in category['subcategories']:
                    if subcat['label'] and subcat['value']:
                        prev_val = f" (Prev: {subcat.get('previous_value', 'N/A')})" if subcat.get('previous_value') else ""
                        print(f"    • {subcat['label']}: {subcat['value']}{prev_val}")
                
                if category.get('total'):
                    prev_total = f" (Prev: {category.get('previous_total', 'N/A')})" if category.get('previous_total') else ""
                    print(f"    💰 Total: {category['total']}{prev_total}")
        
        print("\n" + "="*60)

# Configuration and example usage
def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "api": {
            "endpoint": "https://api.deepseek.com/v1/chat/completions",
            "key": "your-api-key-here",
            "model": "deepseek-chat",
            "temperature": 0.1,
            "max_tokens": 3000,
            "timeout": 30
        },
        "schedule_iii_mapping": {
            "security deposits": "10",
            "long term": "10",
            "advances": "10",
            "deposits": "10",
            "consumables": "11",
            "inventory": "11",
            "raw materials": "11",
            "finished goods": "11",
            "work in progress": "11",
            "stores": "11",
            "cash": "12",
            "bank": "12",
            "trade receivables": "13",
            "debtors": "13",
            "short term loans": "14",
            "short term advances": "14",
            "other current assets": "15",
            "prepaid expenses": "15",
            "trade payables": "16",
            "creditors": "16",
            "other current liabilities": "17",
            "provisions": "18",
            "employee benefits": "18"
        },
        "note_titles": {
            "10": "Long Term Loans and Advances",
            "11": "Inventories",
            "12": "Cash and Bank Balances",
            "13": "Trade Receivables",
            "14": "Short-term Loans and Advances",
            "15": "Other Current Assets",
            "16": "Trade Payables",
            "17": "Other Current Liabilities",
            "18": "Provisions"
        },
        "formatting": {
            "currency_symbol": "₹",
            "amount_unit": "lakhs",
            "decimal_places": 2,
            "date_format": "%Y-%m-%d",
            "conversion_factor": 100000
        },
        "validation": {
            "required_fields": ["account_name", "amount", "date"],
            "required_note_fields": ["title", "full_title", "structure", "metadata"]
        }
    }
    
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Sample configuration created: config.json")

def main():
    """
    Main function to demonstrate the usage
    """
    print("🚀 Trial Balance to Schedule III Notes Generator")
    print("="*50)
    
    # Create sample config if it doesn't exist
    if not os.path.exists("config.json"):
        create_sample_config()
    
    # Sample trial balance data (this would come from your system)
    tb_data = [
        {"account_name": "Long Term - Security Deposits", "amount": 1000000, "date": "2024-03-31"},
        {"account_name": "Long Term - Security Deposits", "amount": 850000, "date": "2023-03-31"},
        {"account_name": "Consumables", "amount": 300000, "date": "2024-03-31"},
        {"account_name": "Consumables", "amount": 280000, "date": "2023-03-31"},
        {"account_name": "Trade Receivables", "amount": 1500000, "date": "2024-03-31"},
        {"account_name": "Trade Receivables", "amount": 1200000, "date": "2023-03-31"},
        {"account_name": "Cash and Bank Balances", "amount": 500000, "date": "2024-03-31"},
        {"account_name": "Cash and Bank Balances", "amount": 450000, "date": "2023-03-31"}
    ]
    
    print(f"📋 Input Data: {len(tb_data)} trial balance entries")
    
    # Initialize generator with configuration
    generator = TrialBalanceNotesGenerator(config_file="config.json")
    
    try:
        # Generate notes
        notes = generator.generate_notes(tb_data)
        
        # Print summary
        generator.print_notes_summary(notes)
        
        # Save to file
        generator.save_notes_to_file(notes)
        
        print("\n💡 To use with actual LLM:")
        print("1. Edit config.json with your API endpoint and key")
        print("2. Run the script again")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
