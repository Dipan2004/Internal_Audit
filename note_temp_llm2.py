import json
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import re
import sys
from typing import Dict, List, Any, Optional
import pandas as pd
import dspy
from dspy import Signature, InputField, OutputField, ChainOfThought

# Load environment variables
load_dotenv()

class OpenRouterLM(dspy.LM):
    """Custom DSPy Language Model for OpenRouter API"""
    
    def __init__(self, model: str, api_key: str, **kwargs):
        self.model = model
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:3000",
            "X-Title": "DSPy Financial Note Generator"
        }
        self.kwargs = {
            'max_tokens': kwargs.get('max_tokens', 8000),
            'temperature': kwargs.get('temperature', 0.1),
            'top_p': kwargs.get('top_p', 0.9)
        }
        super().__init__(model)
    
    def basic_request(self, prompt: str, **kwargs) -> List[Dict[str, Any]]:
        """Make basic request to OpenRouter API"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a financial reporting expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            **self.kwargs,
            **kwargs
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return [{
                'text': content,
                'logprobs': None,
                'finish_reason': result['choices'][0].get('finish_reason', 'stop')
            }]
        except Exception as e:
            print(f"❌ OpenRouter API Error: {e}")
            return [{'text': '', 'logprobs': None, 'finish_reason': 'error'}]

class FinancialNoteSignature(Signature):
    """DSPy signature for financial note generation"""
    context = InputField(desc="Complete financial context including trial balance data, categories, and totals")
    template = InputField(desc="JSON template structure for the financial note")
    note_info = InputField(desc="Note number, title, and classification information")
    
    financial_note_json = OutputField(desc="Complete JSON structure for the financial note following the exact template format")

class FinancialNoteGenerator(dspy.Module):
    """DSPy module for generating financial notes with validation"""
    
    def __init__(self):
        super().__init__()
        self.generate_note = ChainOfThought(FinancialNoteSignature)
    
    def forward(self, context: str, template: str, note_info: str):
        """Generate financial note with DSPy chain of thought"""
        return self.generate_note(
            context=context,
            template=template,
            note_info=note_info
        )

class FlexibleFinancialNoteGenerator:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file")
        
        # Initialize DSPy with OpenRouter
        self.recommended_models = [
            "mistralai/mixtral-8x7b-instruct",  
            "mistralai/mistral-7b-instruct-v0.2" 
        ]
        
        # Initialize DSPy language model
        self.current_model = self.recommended_models[0]
        self.lm = OpenRouterLM(
            model=self.current_model,
            api_key=self.openrouter_api_key,
            max_tokens=8000,
            temperature=0.1
        )
        
        # Configure DSPy
        dspy.settings.configure(lm=self.lm)
        
        # Initialize DSPy module
        self.note_generator = FinancialNoteGenerator()
        
        # Load note templates from note/note_temp.py
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
                "keywords": ["prepaid", "advance", "short term", "employee advance", "supplier advance", "advance tax", "tds", "gst", "statutory"],
                "groups": ["Short Term Loans and Advances", "Current Assets"],
                "exclude_keywords": ["long term", "security deposit"]
            },
            "15": {
                "keywords": ["interest accrued", "accrued income", "other current", "miscellaneous current"],
                "groups": ["Other Current Assets", "Current Assets"],
                "exclude_keywords": ["trade", "advance"]
            }
        }
    
    def load_note_templates(self) -> Dict[str, Any]:
        """Load note templates from note/note_temp.py file."""
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from note.note_temp import note_templates
            return note_templates
        except ImportError as e:
            print(f"❌ Error importing note_templates from note/note_temp.py: {e}")
            return {}
        except Exception as e:
            print(f"❌ Unexpected error loading note_templates: {e}")
            return {}
    
    def load_trial_balance(self, file_path: str = "output/parsed_trial_balance2.json") -> Optional[Dict[str, Any]]:
        """Load the classified trial balance from Excel or JSON."""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        accounts = data
                    elif isinstance(data, dict):
                        accounts = data.get('accounts', [])
                    else:
                        print(f"❌ Unexpected trial balance format: {type(data)}")
                        return None
                    print(f"✅ Loaded trial balance with {len(accounts)} accounts")
                    return {"accounts": accounts}
            elif file_path.endswith('.xlsx'):
                from app.extract import extract_trial_balance_data
                accounts = extract_trial_balance_data(file_path)
                print(f"✅ Extracted trial balance with {len(accounts)} accounts from Excel")
                return {"accounts": accounts}
            else:
                print(f"❌ Unsupported file type: {file_path}")
                return None
        except FileNotFoundError:
            print(f"❌ Trial balance file not found: {file_path}")
            return None
        except Exception as e:
            print(f"❌ Error loading trial balance: {e}")
            return None
    
    def classify_accounts_by_note(self, trial_balance_data: Dict[str, Any], note_number: str) -> List[Dict[str, Any]]:
        """Classify accounts based on note number and patterns"""
        if not trial_balance_data or "accounts" not in trial_balance_data:
            return []
        
        classified_accounts = []
        patterns = self.account_patterns.get(note_number, {})
        keywords = patterns.get("keywords", [])
        groups = patterns.get("groups", [])
        exclude_keywords = patterns.get("exclude_keywords", [])
        
        for account in trial_balance_data["accounts"]:
            account_name = account.get("account_name", "").lower()
            account_group = account.get("group", "")
            
            if any(exclude_word.lower() in account_name for exclude_word in exclude_keywords):
                continue
            
            keyword_match = any(keyword.lower() in account_name for keyword in keywords)
            group_match = account_group in groups
            
            if keyword_match or group_match:
                classified_accounts.append(account)
        
        print(f"📋 Classified {len(classified_accounts)} accounts for Note {note_number}")
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
        categories = {
            "prepaid_expenses": [],
            "other_advances": [],
            "advance_tax": [],
            "statutory_balances": [],
            "uncategorized": []
        } if note_number == "14" else {}
        
        for account in accounts:
            account_name = account.get("account_name", "").lower()
            categorized = False
            
            if note_number == "14":
                if "prepaid" in account_name:
                    categories["prepaid_expenses"].append(account)
                    categorized = True
                elif any(word in account_name for word in ["advance tax", "tax advance", "income tax"]):
                    categories["advance_tax"].append(account)
                    categorized = True
                elif any(word in account_name for word in ["tds", "gst", "statutory", "government", "vat", "pf", "esi"]):
                    categories["statutory_balances"].append(account)
                    categorized = True
                elif any(word in account_name for word in ["advance", "deposit", "recoverable", "employee advance", "supplier advance"]):
                    categories["other_advances"].append(account)
                    categorized = True
                
                if not categorized:
                    categories["uncategorized"].append(account)
        
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
    
    def build_llm_prompt(self, note_number: str, trial_balance_data: Dict[str, Any], classified_accounts: List[Dict[str, Any]]) -> Optional[tuple]:
        """Build dynamic LLM prompt based on note template and classified accounts"""
        if note_number not in self.note_templates:
            return None
        
        template = self.note_templates[note_number]
        total_amount, total_lakhs = self.calculate_totals(classified_accounts)
        categories = self.categorize_accounts(classified_accounts, note_number)
        category_totals, grand_total_lakhs = self.calculate_category_totals(categories)
        
        context = {
            "note_info": {
                "number": note_number,
                "title": template.get("title", ""),
                "full_title": template.get("full_title", "")
            },
            "financial_data": {
                "total_accounts": len(classified_accounts),
                "total_amount": total_amount,
                "total_lakhs": total_lakhs,
                "grand_total_lakhs": grand_total_lakhs
            },
            "categories": category_totals,
            "trial_balance": trial_balance_data,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "financial_year": "2023-24"
        }
        
        # Your existing prompt but structured for DSPy
        prompt_instructions = f"""
You are a financial reporting AI system with two roles:
1. ACCOUNTANT — You extract, compute, and classify data from the financial context and trial balance.
2. AUDITOR — You review the Accountant's output for accuracy, assumptions, and consistency with reporting standards.

Your task is to generate a financial note titled: "{template['full_title']}" strictly following the JSON structure below, based on the provided financial context and trial balance data.

--- *CRITICAL RULES*
- Respond ONLY with a valid JSON object (no markdown, no explanations).
- If a value is unavailable or not calculable, use 0.0.
- Convert all ₹ amounts to lakhs by dividing by 100000 and round to 2 decimal places.
- Ensure that category subtotals *match* the grand total.
- Return a key markdown_content containing a markdown-formatted table for this note.
- Validate that your JSON structure matches the TEMPLATE STRUCTURE exactly.
- Perform intelligent classification: if an entry from the trial balance clearly fits a category, assign it logically.
- If data is ambiguous, make a conservative estimate, and record it in an assumptions field inside the JSON.

--- *CATEGORY RULES FOR NOTE 14 (Short Term Loans and Advances):*
- Categorize entries under:
  - Unsecured, considered good:
    - Prepaid Expenses
    - Other Advances
  - Other loans and advances:
    - Advance Tax
    - Balances with statutory/government authorities
- Use logical inference to map trial balance entries into these subcategories
- If values for March 31, 2023 are missing, default to 0
- Ensure the sum of all subcategories = Total

--- *REQUIRED OUTPUT JSON FORMAT*
- The JSON must include:
  - All categories and subcategories with March 2024 and March 2023 values
  - A computed grand_total_lakhs
  - A markdown_content with the financial note table
  - A generated_on timestamp
  - An assumptions field (optional, if any data was inferred or missing)

Generate the final JSON now:
"""
        
        return (
            json.dumps(context, indent=2),
            json.dumps(template, indent=2),
            prompt_instructions
        )
    
    def call_dspy_api(self, context: str, template: str, note_info: str) -> Optional[str]:
        """Make DSPy API call with model fallback"""
        for model in self.recommended_models:
            print(f"🤖 Trying DSPy with model: {model}")
            try:
                # Update the language model
                self.lm.model = model
                dspy.settings.configure(lm=self.lm)
                
                # Call DSPy module
                result = self.note_generator(
                    context=context,
                    template=template,
                    note_info=note_info
                )
                
                if result and hasattr(result, 'financial_note_json'):
                    print(f"✅ Successful response from DSPy with {model}")
                    return result.financial_note_json
                
            except Exception as e:
                print(f"❌ Failed with DSPy model {model}: {e}")
                continue
        
        print("❌ All DSPy models failed")
        return None
    
    def extract_json_from_markdown(self, response_text: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Extract JSON from response, handling markdown code blocks"""
        response_text = response_text.strip()
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'(\{.*\})'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    json_data = json.loads(match.group(1))
                    return json_data, match.group(1)
                except json.JSONDecodeError:
                    continue
        
        try:
            json_data = json.loads(response_text)
            return json_data, response_text
        except json.JSONDecodeError:
            return None, None
    
    def validate_json_structure(self, json_data: Dict[str, Any], note_number: str) -> bool:
        """Validate generated JSON structure against template"""
        if note_number not in self.note_templates:
            return False
        
        template = self.note_templates[note_number]
        required_keys = set(template.keys())
        actual_keys = set(json_data.keys())
        
        missing_keys = required_keys - actual_keys
        if missing_keys:
            print(f"⚠ Missing keys in generated JSON: {missing_keys}")
            return False
        
        # Validate totals for Note 14
        if note_number == "14" and "data" in json_data:
            try:
                data = json_data["data"]
                if "2024" in data:
                    categories_2024 = data["2024"]
                    subtotal = sum(float(v) for k, v in categories_2024.items() if k != "total")
                    total = float(categories_2024.get("total", 0))
                    if abs(subtotal - total) > 0.01:  # Allow small rounding differences
                        print(f"⚠ Total mismatch: subtotal={subtotal}, total={total}")
                        return False
            except Exception as e:
                print(f"⚠ Error validating totals: {e}")
                return False
        
        print("✅ JSON structure validation passed")
        return True
    
    def save_generated_note(self, note_data: str, note_number: str, output_dir: str = "generated_notes") -> bool:
        """Save the generated note to file in both JSON and markdown formats"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        json_output_path = f"{output_dir}/note_{note_number}.json"
        raw_output_path = f"{output_dir}/note_{note_number}_raw.txt"
        formatted_md_path = f"{output_dir}/note_{note_number}_formatted.md"
        
        try:
            with open(raw_output_path, 'w', encoding='utf-8') as f:
                f.write(note_data)
            
            json_data, json_string = self.extract_json_from_markdown(note_data)
            if json_data:
                # Validate JSON structure
                is_valid = self.validate_json_structure(json_data, note_number)
                
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"✅ JSON saved to {json_output_path} {'(validated)' if is_valid else '(validation issues)'}")
                
                # Always write markdown file, fallback if missing
                md_content = json_data.get('markdown_content')
                if not md_content:
                    md_content = f"# Note {note_number}\n\n```json\n{json.dumps(json_data, indent=2)}\n```"
                with open(formatted_md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                return is_valid
            else:
                fallback_json = {
                    "note_number": note_number,
                    "raw_response": note_data,
                    "error": "Could not parse JSON from response",
                    "generated_on": datetime.now().isoformat()
                }
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(fallback_json, f, indent=2, ensure_ascii=False)
                print(f"⚠ Fallback JSON saved to {json_output_path}")
                return False
        except Exception as e:
            print(f"❌ Error saving files: {e}")
            return False
    
    def generate_note(self, note_number: str, trial_balance_path: str = "output/parsed_trial_balance2.json") -> bool:
        """Generate a specific note based on note number using DSPy"""
        if note_number not in self.note_templates:
            print(f"❌ Note template {note_number} not found")
            return False
        
        print(f"\n🚀 Starting DSPy Note {note_number} generation...")
        trial_balance = self.load_trial_balance(trial_balance_path)
        if not trial_balance:
            return False
        
        classified_accounts = self.classify_accounts_by_note(trial_balance, note_number)
        prompt_data = self.build_llm_prompt(note_number, trial_balance, classified_accounts)
        if not prompt_data:
            print("❌ Failed to build prompt")
            return False
        
        context, template, note_info = prompt_data
        response = self.call_dspy_api(context, template, note_info)
        if not response:
            print("❌ Failed to get DSPy response")
            return False
        
        success = self.save_generated_note(response, note_number)
        print(f"{'✅' if success else '⚠'} DSPy Note {note_number} {'generated successfully' if success else 'generated with issues'}")
        return success
    
    def generate_all_notes(self, trial_balance_path: str = "output/parsed_trial_balance2.json") -> Dict[str, bool]:
        """Generate all available notes using DSPy"""
        print(f"\n🚀 Starting DSPy generation of all {len(self.note_templates)} notes...")
        results = {}
        for note_number in self.note_templates.keys():
            print(f"\n{'='*60}\n📝 Processing DSPy Note {note_number}\n{'='*60}")
            success = self.generate_note(note_number, trial_balance_path)
            results[note_number] = success
            import time
            time.sleep(1)
        
        print(f"\n{'='*60}\n📊 DSPy GENERATION SUMMARY\n{'='*60}")
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        for note_number, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"Note {note_number}: {status}")
        print(f"\nTotal: {successful}/{total} notes generated successfully with DSPy")
        print(f"📁 Check 'generated_notes' folder for outputs")
        
        return results

def main():
    """Main function to run the DSPy flexible note generator"""
    try:
        generator = FlexibleFinancialNoteGenerator()
        if not generator.note_templates:
            print("❌ No note templates loaded. Check note/note_temp.py")
            return
        
        print(f"✅ Loaded {len(generator.note_templates)} note templates")
        print(f"🤖 DSPy configured with OpenRouter models: {', '.join(generator.recommended_models)}")
        
        choice = input("\nGenerate (1) specific note or (2) all notes? Enter 1 or 2: ").strip()
        
        if choice == "1":
            available_notes = list(generator.note_templates.keys())
            print(f"Available notes: {', '.join(available_notes)}")
            note_number = input("Enter note number: ").strip()
            if note_number in available_notes:
                success = generator.generate_note(note_number)
                print(f"\n{'✅' if success else '⚠'} DSPy Note {note_number} {'generated successfully' if success else 'generated with issues'}")
            else:
                print(f"❌ Note {note_number} not found")
        elif choice == "2":
            results = generator.generate_all_notes()
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            print(f"\n{'✅' if successful == total else '⚠'} {successful}/{total} notes generated successfully with DSPy")
        else:
            print("❌ Invalid choice. Enter 1 or 2.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()