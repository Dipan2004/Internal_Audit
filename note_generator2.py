import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

<<<<<<< HEAD

load_dotenv()

class FlexibleFinancialNoteGenerator:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:3000",
            "X-Title": "Financial Note Generator"
        }
        
        
        self.note_templates = self.load_note_templates()
        
        # Account classification patterns
        self.account_patterns = {
            "10": {
                "keywords": ["security deposit", "long term advance", "deposit", "advance recoverable"],
                "groups": ["Long Term Loans and Advances", "Non-Current Assets"],
                "exclude_keywords": ["short term", "current", "trade"]
            },
            "11": {
                "keywords": ["inventory", "stock", "raw material", "finished goods", "work in progress", "consumables"],
                "groups": ["Inventories", "Current Assets"],
                "exclude_keywords": ["advance", "deposit"]
            },
            "12": {
                "keywords": ["trade receivable", "debtors", "accounts receivable", "sundry debtors"],
                "groups": ["Trade Receivables", "Current Assets"],
                "exclude_keywords": ["advance", "deposit"]
            },
            "13": {
                "keywords": ["cash", "bank", "petty cash", "cash on hand", "current account", "savings account", "fixed deposit"],
                "groups": ["Cash and Bank Balances", "Current Assets"],
                "exclude_keywords": ["advance", "loan"]
            },
            "14": {
                "keywords": ["prepaid", "advance", "short term", "employee advance", "supplier advance", "advance tax", "tds"],
                "groups": ["Short Term Loans and Advances", "Current Assets"],
                "exclude_keywords": ["long term", "security deposit", "deposit", "gst", "tcs"]
            },
            "15": {
                "keywords": ["interest accrued", "accrued income", "other current", "miscellaneous current"],
                "groups": ["Other Current Assets", "Current Assets"],
                "exclude_keywords": ["trade", "advance"]
            }
        }
        
        
=======
class TrialBalanceNotesGenerator:
    def __init__(self, config_file: str = "config.json"):
        """Initialize with configuration and recommended models."""
        self.config = self._load_config(config_file)
>>>>>>> a1d41f0 (llm note temp generator partialy working)
        self.recommended_models = [
            "deepseek/deepseek-r1:free",
            "deepseek/deepseek-chat-v3-0324:free"
        ]
        
        # API configuration
        self.api_endpoint = self.config.get('api', {}).get('endpoint', 'https://openrouter.ai/api/v1/chat/completions')
        self.api_key = self.config.get('api', {}).get('key')
        self.model = self.config.get('api', {}).get('model', self.recommended_models[0])
        
<<<<<<< HEAD
        for account in trial_balance_data["accounts"]:
            account_name = account.get("account_name", "").lower()
            account_group = account.get("group", "")
            amount = account.get("amount", 0)
            
            
            if amount == 0:
                continue
                
            
            if any(exclude_word.lower() in account_name for exclude_word in exclude_keywords):
                continue
            
            
            keyword_match = any(keyword.lower() in account_name for keyword in keywords)
            group_match = account_group in groups
            
            if keyword_match or group_match:
                
                if note_number == "14" and account_name in ["deposits (asset)", "gst input tax credit", "tcs receivables", "advance to perennail code it consultants pvt ltd"]:
                    continue
                if note_number == "10" and account_name in ["prepaid expenses", "loans & advances (asset)", "tds advance tax paid sec 100", "tds receivables"]:
                    continue
                classified_accounts.append(account)
        
        print(f"📋 Classified {len(classified_accounts)} accounts for Note {note_number}: {[acc['account_name'] for acc in classified_accounts]}")
        return classified_accounts
    
    def safe_amount_conversion(self, amount: Any, conversion_factor: float = 100000) -> float:
        """Safely convert amount to lakhs"""
        try:
            if isinstance(amount, str):
                cleaned = re.sub(r'[^\d.-]', '', amount)
                amount_float = float(cleaned) if cleaned else 0.0
            else:
                amount_float = float(amount) if amount is not None else 0.0
            return round(amount_float / conversion_factor, 2)
        except (ValueError, TypeError):
            return 0.0
    
    def calculate_totals(self, accounts: List[Dict[str, Any]], conversion_factor: float = 100000) -> tuple[float, float]:
        """Calculate totals with safe amount conversion"""
        total_amount = 0.0
        for account in accounts:
            amount = self.safe_amount_conversion(account.get("amount", 0), 1)
            total_amount += amount
        total_lakhs = round(total_amount / conversion_factor, 2)
        return total_amount, total_lakhs
    
    def categorize_accounts(self, accounts: List[Dict[str, Any]], note_number: str) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize accounts based on note-specific rules"""
        categories = {}
        
        if note_number == "10":
            categories = {
                "security_deposits": [],
                "uncategorized": []
            }
            for account in accounts:
                account_name = account.get("account_name", "").lower()
                if any(word in account_name for word in ["deposit", "security deposit"]):
                    categories["security_deposits"].append(account)
                else:
                    categories["uncategorized"].append(account)
        
        elif note_number == "11":
            categories = {
                "consumables": [],
                "uncategorized": []
            }
            for account in accounts:
                account_name = account.get("account_name", "").lower()
                if "consumables" in account_name:
                    categories["consumables"].append(account)
                else:
                    categories["uncategorized"].append(account)
        
        elif note_number == "12":
            categories = {
                "over_six_months": [],
                "other_receivables": [],
                "uncategorized": []
            }
            for account in accounts:
                account_name = account.get("account_name", "").lower()
                # Note: Assuming no aging data in trial balance; categorize all as other_receivables
                categories["other_receivables"].append(account)
        
        elif note_number == "13":
            categories = {
                "bank_balances": [],
                "cash_on_hand": [],
                "fixed_deposits": [],
                "uncategorized": []
            }
            for account in accounts:
                account_name = account.get("account_name", "").lower()
                if any(word in account_name for word in ["bank", "current account", "savings account"]):
                    categories["bank_balances"].append(account)
                elif "cash" in account_name:
                    categories["cash_on_hand"].append(account)
                elif "fixed deposit" in account_name:
                    categories["fixed_deposits"].append(account)
                else:
                    categories["uncategorized"].append(account)
        
        elif note_number == "14":
            categories = {
                "prepaid_expenses": [],
                "other_advances": [],
                "advance_tax": [],
                "statutory_balances": [],
                "uncategorized": []
            }
            for account in accounts:
                account_name = account.get("account_name", "").lower()
                if "prepaid expenses" in account_name:
                    categories["prepaid_expenses"].append(account)
                elif "loans & advances (asset)" in account_name:
                    categories["other_advances"].append(account)
                elif any(word in account_name for word in ["advance tax", "tax advance", "income tax"]):
                    categories["advance_tax"].append(account)
                elif "tds receivables" in account_name:
                    categories["statutory_balances"].append(account)
                else:
                    categories["uncategorized"].append(account)
        
        elif note_number == "15":
            categories = {
                "interest_accrued": [],
                "uncategorized": []
            }
            for account in accounts:
                account_name = account.get("account_name", "").lower()
                if "interest accrued" in account_name:
                    categories["interest_accrued"].append(account)
                else:
                    categories["uncategorized"].append(account)
        
        
        for category, acc_list in categories.items():
            if acc_list:
                print(f" Category '{category}' for Note {note_number}: {[acc['account_name'] for acc in acc_list]}")
            elif category != "uncategorized":
                print(f" Category '{category}' for Note {note_number}: Empty")
        
        if categories.get("uncategorized", []):
            print(f"⚠ Uncategorized accounts for Note {note_number}: {[acc['account_name'] for acc in categories['uncategorized']]}")
        
        return categories
    
    def calculate_category_totals(self, categories: Dict[str, List[Dict[str, Any]]], conversion_factor: float = 100000) -> tuple[Dict[str, Dict[str, Any]], float]:
        """Calculate totals for each category"""
        category_totals = {}
        grand_total = 0.0
        
        for category_name, accounts in categories.items():
            if not isinstance(accounts, list):
                continue
            total_amount = 0.0
            for account in accounts:
                amount = self.safe_amount_conversion(account.get("amount", 0), 1)
                total_amount += amount
            total_lakhs = round(total_amount / conversion_factor, 2)
            category_totals[category_name] = {
                "amount": total_amount,
                "lakhs": total_lakhs,
                "count": len(accounts),
                "accounts": [acc.get("account_name", "") for acc in accounts]
            }
            grand_total += total_amount
        
        return category_totals, round(grand_total / conversion_factor, 2)
    
    def build_llm_prompt(self, note_number: str, trial_balance_data: Dict[str, Any], classified_accounts: List[Dict[str, Any]]) -> Optional[str]:
        """Build dynamic LLM prompt based on note template and classified accounts"""
        if note_number not in self.note_templates:
            return None
        
        template = self.note_templates[note_number]
        total_amount, total_lakhs = self.calculate_totals(classified_accounts)
        categories = self.categorize_accounts(classified_accounts, note_number)
        category_totals, grand_total_lakhs = self.calculate_category_totals(categories)
        
        # Prepare data for template
        llm_data = {
            f"{note_number}_march_2024_total": str(grand_total_lakhs),
            f"{note_number}_march_2023_total": "0.00",
            f"{note_number}_total_2024": str(grand_total_lakhs),
            f"{note_number}_total_2023": "0.00"
=======
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else None,
            "HTTP-Referer": "https://github.com/your-repo",  # Required for OpenRouter
            "X-Title": "Trial Balance Generator"
>>>>>>> a1d41f0 (llm note temp generator partialy working)
        }
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration with smart defaults."""
        default_config = {
            "api": {
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "key": None,
                "model": "deepseek/deepseek-r1:free",
                "temperature": 0.1,
                "max_tokens": 3000,
                "timeout": 30
            },
            "schedule_iii_mapping": {
                "share capital": "2", "reserves": "3", "surplus": "3", 
                "borrowings": "4", "deferred tax": "5", "payables": "6", 
                "creditors": "6", "liabilities": "7", "provisions": "8",
                "fixed assets": "9", "assets": "9", "deposits": "10", 
                "advances": "10", "inventory": "11", "consumables": "11",
                "cash": "12", "bank": "12", "receivables": "13", 
                "debtors": "13", "loans": "14"
            },
            "note_titles": {
                "2": "Share Capital", "3": "Reserves and Surplus",
                "4": "Long Term Borrowings", "5": "Deferred Tax Liabilities",
                "6": "Trade Payables", "7": "Other Current Liabilities",
                "8": "Short Term Provisions", "9": "Fixed Assets",
                "10": "Long Term Loans and Advances", "11": "Inventories",
                "12": "Cash and Bank Balances", "13": "Trade Receivables",
                "14": "Short-term Loans and Advances", "15": "Other Current Assets"
            },
            "formatting": {
                "currency_symbol": "₹",
                "amount_unit": "lakhs",
                "decimal_places": 2,
                "conversion_factor": 100000
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ Config error: {e}. Using defaults.")
        else:
            self._save_config(default_config, config_file)
        
        return default_config
    
    def _save_config(self, config: Dict[str, Any], config_file: str):
        """Save configuration file."""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Config saved: {config_file}")
        except Exception as e:
            print(f"❌ Config save error: {e}")
    
    def load_trial_balance(self, filename: str = "output/parsed_trial_balance.json") -> List[Dict]:
        """Load trial balance data with smart parsing and multiple file fallbacks."""
        # Try multiple common file locations
        possible_files = [
            filename,
            "parsed_trial_balance.json",
            "trial_balance.json",
            "output/trial_balance.json",
            "data/parsed_trial_balance.json"
        ]
        
        for file_path in possible_files:
            if os.path.exists(file_path):
                print(f"📁 Found file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        rows = data
                    elif isinstance(data, dict) and 'sheets' in data:
                        rows = []
                        for sheet in data['sheets']:
                            if any(keyword in sheet.get('name', '').lower() 
                                  for keyword in ['trial', 'balance', 'tally']):
                                rows.extend(sheet.get('rows', []))
                    else:
                        print(f"⚠️ Unexpected JSON structure in {file_path}")
                        continue
                    
                    # Process rows
                    tb_data = []
                    for row in rows:
                        account_name = row.get('Particulars', '').strip()
                        if not account_name:
                            continue
                        
                        # Get amounts with multiple field name options
                        debit = float(row.get('Debit', 0) or row.get('Opening', 0) or 
                                    row.get('Dr', 0) or row.get('Debit Amount', 0) or 0)
                        credit = float(row.get('Credit', 0) or row.get('Closing', 0) or 
                                     row.get('Cr', 0) or row.get('Credit Amount', 0) or 0)
                        amount = debit - credit
                        
                        if amount != 0:
                            tb_data.append({
                                'account_name': account_name,
                                'amount': amount,
                                'date': row.get('date', '2024-03-31'),
                                'debit_credit': 'Debit' if amount > 0 else 'Credit',
                                'year': '2023-24'  # Default year
                            })
                    
                    if tb_data:
                        print(f"✅ Successfully loaded {len(tb_data)} entries from {file_path}")
                        return tb_data
                    else:
                        print(f"⚠️ No valid data found in {file_path}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON in {file_path}")
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")
        
        # If no file found, create sample data
        print("📝 No trial balance file found. Creating sample data...")
        return self._create_sample_data()
    
    def _create_sample_data(self) -> List[Dict]:
        """Create sample trial balance data for testing."""
        sample_data = [
            {'account_name': 'Share Capital', 'amount': 54252000, 'date': '2024-03-31', 'debit_credit': 'Credit', 'year': '2023-24'},
            {'account_name': 'Reserves & Surplus', 'amount': 25000000, 'date': '2024-03-31', 'debit_credit': 'Credit', 'year': '2023-24'},
            {'account_name': 'Trade Payables', 'amount': -5000000, 'date': '2024-03-31', 'debit_credit': 'Credit', 'year': '2023-24'},
            {'account_name': 'Fixed Assets', 'amount': 45000000, 'date': '2024-03-31', 'debit_credit': 'Debit', 'year': '2023-24'},
            {'account_name': 'Cash and Bank', 'amount': 13125000, 'date': '2024-03-31', 'debit_credit': 'Debit', 'year': '2023-24'},
            {'account_name': 'Trade Receivables', 'amount': 8000000, 'date': '2024-03-31', 'debit_credit': 'Debit', 'year': '2023-24'},
            {'account_name': 'Inventory', 'amount': 992000, 'date': '2024-03-31', 'debit_credit': 'Debit', 'year': '2023-24'},
            {'account_name': 'Security Deposits', 'amount': 8181000, 'date': '2024-03-31', 'debit_credit': 'Debit', 'year': '2023-24'}
        ]
        
        # Save sample data for future use
        os.makedirs('output', exist_ok=True)
        with open('output/parsed_trial_balance.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Sample trial balance data created at output/parsed_trial_balance.json")
        return sample_data
    
    def categorize_account(self, account_name: str) -> str:
        """Categorize account to Schedule III note number."""
        account_lower = account_name.lower()
        mapping = self.config['schedule_iii_mapping']
        
        for keyword, note_num in mapping.items():
            if keyword in account_lower:
                return note_num
        return "15"  # Default to Other Current Assets
    
    def format_amount(self, amount: float) -> str:
        """Format amount to lakhs with proper decimal places."""
        formatting = self.config['formatting']
        amount_in_lakhs = amount / formatting['conversion_factor']
        return f"{amount_in_lakhs:.{formatting['decimal_places']}f}"
    
    def build_prompt(self, tb_data: List[Dict]) -> str:
        """Build concise prompt for LLM."""
        if not tb_data:
            return ""
        
        # Group accounts by category
        categories = {}
        for entry in tb_data:
            note_num = self.categorize_account(entry['account_name'])
            if note_num not in categories:
                categories[note_num] = []
            categories[note_num].append(entry)
        
        # Format data
        formatted_data = []
        for note_num, entries in categories.items():
            note_title = self.config['note_titles'].get(note_num, 'Other')
            formatted_data.append(f"Note {note_num} - {note_title}:")
            for entry in entries:
                amount = self.format_amount(entry['amount'])
                formatted_data.append(f"  {entry['account_name']}: ₹{amount} lakhs")
        
        data_str = "\n".join(formatted_data)
        
        return f"""Generate Schedule III notes for Indian companies from this trial balance data:

{data_str}

Return ONLY valid JSON in this format:
{{
  "note_number": {{
    "title": "Note Title",
    "full_title": "Note X. Full Title",
    "structure": [
      {{
        "category": "In Lakhs",
        "subcategories": [
          {{"label": "Account Name", "value": "amount"}},
          {{"label": "March 31, 2024", "value": "total"}}
        ],
        "total": "category_total"
      }}
    ],
    "metadata": {{"note_number": "X", "generated_on": "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}}
  }}
}}

Rules:
- Use provided amounts in lakhs (already converted)
- Group similar accounts logically
- Calculate accurate totals
- Follow Schedule III format
- No additional text, only JSON"""
    
    def call_llm(self, prompt: str) -> str:
        """Call LLM with improved error handling."""
        if not self.api_key:
            print("⚠️ No API key found. Using mock response.")
            return self._generate_mock_response()
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert CA. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config['api']['temperature'],
            "max_tokens": self.config['api']['max_tokens']
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.config['api']['timeout']
            )
            
            if response.status_code == 401:
                print("❌ API key invalid. Check your configuration.")
                return self._generate_mock_response()
            
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
            elif 'response' in result:
                return result['response']
            else:
                print("⚠️ Unexpected response format. Using mock.")
                return self._generate_mock_response()
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API call failed: {e}")
            return self._generate_mock_response()
    
    def _generate_mock_response(self) -> str:
        """Generate mock response for testing."""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        mock_response = {
            "12": {
                "title": "Cash and Bank Balances",
                "full_title": "12. Cash and Bank Balances",
                "structure": [
                    {
                        "category": "In Lakhs",
                        "subcategories": [
                            {"label": "Cash in Hand", "value": "5.50"},
                            {"label": "Bank Balance", "value": "125.75"},
                            {"label": "March 31, 2024", "value": "131.25"}
                        ],
                        "total": "131.25"
                    }
                ],
                "metadata": {
                    "note_number": "12",
                    "generated_on": current_time
                }
            }
        }
        
        return json.dumps(mock_response, indent=2)
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response with robust error handling."""
        try:
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Parse JSON
            parsed = json.loads(response)
            
            # Validate structure
            if not isinstance(parsed, dict):
                raise ValueError("Response must be a JSON object")
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return {}
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return {}
    
    def generate_notes(self, tb_filename: str = "output/parsed_trial_balance.json") -> Dict[str, Any]:
        """Main method - generate Schedule III notes."""
        print("🚀 Generating Schedule III Notes...")
        
        # Load data
        tb_data = self.load_trial_balance(tb_filename)
        if not tb_data:
            print("❌ No trial balance data found.")
            return {}
        
        print(f"📋 Loaded {len(tb_data)} entries")
        
        # Show sample of loaded data
        print("\n📊 Sample of loaded accounts:")
        for i, entry in enumerate(tb_data[:5]):
            amount_formatted = self.format_amount(entry['amount'])
            print(f"  {i+1}. {entry['account_name']}: ₹{amount_formatted} lakhs ({entry['debit_credit']})")
        if len(tb_data) > 5:
            print(f"  ... and {len(tb_data) - 5} more accounts")
        
        # Build prompt
        prompt = self.build_prompt(tb_data)
        if not prompt:
            print("❌ Failed to build prompt.")
            return {}
        
        # Call LLM
        print("\n🤖 Calling LLM...")
        response = self.call_llm(prompt)
        
        # Parse response
        notes = self.parse_response(response)
        
        if notes:
            print(f"✅ Generated {len(notes)} notes")
            self.save_notes(notes)
            self.print_summary(notes)
        else:
            print("❌ Failed to generate notes.")
        
        return notes
    
    def save_notes(self, notes: Dict[str, Any], filename: str = "schedule_iii_notes.json"):
        """Save notes to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            print(f"💾 Notes saved: {filename}")
        except Exception as e:
            print(f"❌ Save error: {e}")
    
    def print_summary(self, notes: Dict[str, Any]):
        """Print concise summary."""
        print("\n📊 SCHEDULE III NOTES SUMMARY")
        print("=" * 50)
        
        for note_num, note_data in notes.items():
            print(f"\n{note_data.get('full_title', f'Note {note_num}')}")
            print("-" * 30)
            
            for structure in note_data.get('structure', []):
                for subcat in structure.get('subcategories', []):
                    label = subcat.get('label', '')
                    value = subcat.get('value', '')
                    if label and value:
                        print(f"  • {label}: ₹{value} lakhs")
                
                total = structure.get('total')
                if total:
                    print(f"  💰 Total: ₹{total} lakhs")
        
        print("\n" + "=" * 50)

def setup_config():
    """Create sample configuration."""
    config = {
        "api": {
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "key": "your-openrouter-api-key-here",
            "model": "deepseek/deepseek-r1:free",
            "temperature": 0.1,
            "max_tokens": 3000,
            "timeout": 30
        }
    }
    
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Configuration created: config.json")
    print("📝 Edit config.json with your OpenRouter API key")

def main():
    """Main execution function."""
    print("🚀 Trial Balance → Schedule III Notes Generator")
    print("=" * 50)
    
    if not os.path.exists("config.json"):
        setup_config()
        print("\n⚠️ Please edit config.json with your API key, then run again.")
        return
    
    try:
        generator = TrialBalanceNotesGenerator()
        notes = generator.generate_notes()
        
        if notes:
            print(f"\n🎉 Success! Generated {len(notes)} Schedule III notes.")
            print("📁 Files created:")
            print("  - schedule_iii_notes.json (Generated notes)")
            print("  - output/parsed_trial_balance.json (Sample data)")
        else:
            print("\n💡 Setup Instructions:")
            print("1. Get API key from https://openrouter.ai/")
            print("2. Edit config.json with your API key")
            print("3. Place trial balance data in output/parsed_trial_balance.json")
            print("4. Run script again")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
<<<<<<< HEAD
    generator = FlexibleFinancialNoteGenerator()
    generator.generate_all_notes()
=======
    main()
>>>>>>> a1d41f0 (llm note temp generator partialy working)
