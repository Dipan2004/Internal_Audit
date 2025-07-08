import json
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import re
import sys
from typing import Dict, List, Any, Optional

# Load environment variables
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
        
        # Load note templates from note_temp.py
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
        
        # Recommended models
        self.recommended_models = [
            "deepseek/deepseek-r1:free",
            "deepseek/deepseek-chat-v3-0324:free"
        ]
    
    def load_note_templates(self) -> Dict[str, Any]:
        """Load note templates from note/note_temp.py file"""
        try:
            sys.path.append('note')
            from note_temp import note_templates
            return note_templates
        except ImportError:
            try:
                with open('note/note_temp.py', 'r') as f:
                    content = f.read()
                    exec_globals = {}
                    exec(content, exec_globals)
                    return exec_globals.get('note_templates', {})
            except FileNotFoundError:
                print("Warning: note/note_temp.py not found. Using empty templates.")
                return {}
    
    def load_trial_balance(self, file_path: str = "output/parsed_trial_balance.json") -> Optional[Dict[str, Any]]:
        """Load the classified trial balance JSON file"""
        try:
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
        except FileNotFoundError:
            print(f"❌ Trial balance file not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing trial balance JSON: {e}")
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
            amount = account.get("amount", 0)
            
            # Skip accounts with zero amount
            if amount == 0:
                continue
                
            # Check for exclusion keywords
            if any(exclude_word.lower() in account_name for exclude_word in exclude_keywords):
                continue
            
            # Check for keyword or group match
            keyword_match = any(keyword.lower() in account_name for keyword in keywords)
            group_match = account_group in groups
            
            if keyword_match or group_match:
                # Additional exclusions for specific notes
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
        
        # Log categorized accounts for debugging
        for category, acc_list in categories.items():
            if acc_list:
                print(f"📋 Category '{category}' for Note {note_number}: {[acc['account_name'] for acc in acc_list]}")
            elif category != "uncategorized":
                print(f"📋 Category '{category}' for Note {note_number}: Empty")
        
        if categories.get("uncategorized", []):
            print(f"⚠️ Uncategorized accounts for Note {note_number}: {[acc['account_name'] for acc in categories['uncategorized']]}")
        
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
        }
        
        # Map category totals to template placeholders
        if note_number == "10":
            llm_data.update({
                "10_security_deposits_2024": str(category_totals.get("security_deposits", {}).get("lakhs", 0.00)),
                "10_security_deposits_2023": "0.00",
                "10_unsecured_total_2024": str(category_totals.get("security_deposits", {}).get("lakhs", 0.00)),
                "10_unsecured_total_2023": "0.00"
            })
        elif note_number == "11":
            llm_data.update({
                "11_consumables_2024": str(category_totals.get("consumables", {}).get("lakhs", 0.00)),
                "11_consumables_2023": "0.00"
            })
        elif note_number == "12":
            llm_data.update({
                "12_over_six_months_2024": "0.00",  # No aging data in trial balance
                "12_over_six_months_2023": "0.00",
                "12_other_receivables_2024": str(category_totals.get("other_receivables", {}).get("lakhs", 0.00)),
                "12_other_receivables_2023": "0.00",
                "12_unsecured_total_2024": str(category_totals.get("other_receivables", {}).get("lakhs", 0.00)),
                "12_unsecured_total_2023": "0.00",
                # Placeholder for aging analysis (all 0.00 due to lack of data)
                "12_zero_six_2024": "0.00",
                "12_six_one_2024": "0.00",
                "12_one_two_2024": "0.00",
                "12_two_three_2024": "0.00",
                "12_more_three_2024": "0.00",
                "12_age_total_2024": str(category_totals.get("other_receivables", {}).get("lakhs", 0.00)),
                "12_zero_six_2023": "0.00",
                "12_six_one_2023": "0.00",
                "12_one_two_2023": "0.00",
                "12_two_three_2023": "0.00",
                "12_more_three_2023": "0.00",
                "12_age_total_2023": "0.00",
                "12_undisputed_good_zero_six_2024": "0.00",
                "12_undisputed_good_six_one_2024": "0.00",
                "12_undisputed_good_one_two_2024": "0.00",
                "12_undisputed_good_two_three_2024": "0.00",
                "12_undisputed_good_more_three_2024": "0.00",
                "12_undisputed_good_total_2024": str(category_totals.get("other_receivables", {}).get("lakhs", 0.00)),
                # Add other aging placeholders as needed
            })
        elif note_number == "13":
            llm_data.update({
                "13_bank_balances_2024": str(category_totals.get("bank_balances", {}).get("lakhs", 0.00)),
                "13_bank_balances_2023": "0.00",
                "13_cash_on_hand_2024": str(category_totals.get("cash_on_hand", {}).get("lakhs", 0.00)),
                "13_cash_on_hand_2023": "0.00",
                "13_fixed_deposits_2024": str(category_totals.get("fixed_deposits", {}).get("lakhs", 0.00)),
                "13_fixed_deposits_2023": "0.00",
                "13_total_2024": str(grand_total_lakhs),
                "13_total_2023": "0.00"
            })
        elif note_number == "14":
            llm_data.update({
                "14_prepaid_expenses_2024": str(category_totals.get("prepaid_expenses", {}).get("lakhs", 0.00)),
                "14_prepaid_expenses_2023": "0.00",
                "14_other_advances_2024": str(category_totals.get("other_advances", {}).get("lakhs", 0.00)),
                "14_other_advances_2023": "0.00",
                "14_advance_tax_2024": str(category_totals.get("advance_tax", {}).get("lakhs", 0.00)),
                "14_advance_tax_2023": "0.00",
                "14_statutory_balances_2024": str(category_totals.get("statutory_balances", {}).get("lakhs", 0.00)),
                "14_statutory_balances_2023": "0.00"
            })
        elif note_number == "15":
            llm_data.update({
                "15_interest_accrued_2024": str(category_totals.get("interest_accrued", {}).get("lakhs", 0.00)),
                "15_interest_accrued_2023": "0.00"
            })
        
        # Generate template with filled values
        from note_temp import generate_note_template
        filled_template = generate_note_template(note_number, llm_data)
        
        # Generate markdown content dynamically
        markdown_content = ""
        if note_number == "14":
            markdown_content = f"""14. Short Term Loans and Advances

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Unsecured, considered good**|                |                |
| Prepaid Expenses             | {category_totals.get("prepaid_expenses", {}).get("lakhs", 0.00)} | - |
| Other Advances               | {category_totals.get("other_advances", {}).get("lakhs", 0.00)} | - |
| **Other loans and advances** |                |                |
| Advance tax                  | {category_totals.get("advance_tax", {}).get("lakhs", 0.00)} | - |
| Balances with statutory/government authorities | {category_totals.get("statutory_balances", {}).get("lakhs", 0.00)} | - |
| **Total**                    | {grand_total_lakhs} | - |
"""
        elif note_number == "10":
            markdown_content = f"""10. Long Term Loans and Advances

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Unsecured, considered good**|                |                |
| Security Deposits            | {category_totals.get("security_deposits", {}).get("lakhs", 0.00)} | - |
| **Total**                    | {grand_total_lakhs} | - |
"""
        elif note_number == "11":
            markdown_content = f"""11. Inventories

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Consumables                  | {category_totals.get("consumables", {}).get("lakhs", 0.00)} | - |
| **Total**                    | {grand_total_lakhs} | - |
"""
        elif note_number == "12":
            markdown_content = f"""12. Trade Receivables

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Unsecured, considered good**|                |                |
| Other receivables            | {category_totals.get("other_receivables", {}).get("lakhs", 0.00)} | - |
| **Total**                    | {grand_total_lakhs} | - |
"""
        elif note_number == "13":
            markdown_content = f"""13. Cash and Bank Balances

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Cash and cash equivalents**|                |                |
| Balances with banks in current accounts | {category_totals.get("bank_balances", {}).get("lakhs", 0.00)} | - |
| Cash on hand                 | {category_totals.get("cash_on_hand", {}).get("lakhs", 0.00)} | - |
| **Other Bank Balances**      |                |                |
| Fixed Deposits               | {category_totals.get("fixed_deposits", {}).get("lakhs", 0.00)} | - |
| **Total**                    | {grand_total_lakhs} | - |
"""
        elif note_number == "15":
            markdown_content = f"""15. Other Current Assets

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Interest accrued on fixed deposits | {category_totals.get("interest_accrued", {}).get("lakhs", 0.00)} | - |
| **Total**                    | {grand_total_lakhs} | - |
"""
        
        context = {
            "note_info": {
                "number": note_number,
                "title": template.get("title", ""),
                "full_title": template.get("full_title", "")
            },
            "financial_data": {
                "total_accounts": len(classified_accounts),
                "total_amount": total_amount,
                "total_lakhs": grand_total_lakhs,
                "category_totals": category_totals
            },
            "trial_balance": trial_balance_data,
            "current_date": datetime.now().isoformat(),
            "financial_year": "2023-24"
        }
        
        prompt = f"""
You are a financial reporting expert. Generate a JSON object for "{template['full_title']}" following the exact template structure provided.

**CRITICAL INSTRUCTIONS:**
1. Return ONLY valid JSON - no markdown formatting, no explanations
2. Follow the exact template structure provided
3. All amounts must be in lakhs (₹ in lakhs, divide by 100000, round to 2 decimal places)
4. Use provided category totals for accurate values
5. For 2023 data (previous year), use 0 or "-"
6. Ensure totals add up correctly
7. Include markdown_content for each note with the specified table format
8. Use professional financial reporting standards
9. Exclude accounts like 'Deposits (Asset)', 'GST Input Tax Credit', 'TCS Receivables', and 'Advance to Perennail Code IT Consultants Pvt Ltd' from Note 14
10. Use trial balance data and calculated category totals for all values

**TEMPLATE STRUCTURE:**
{json.dumps(filled_template, indent=2)}

**FINANCIAL CONTEXT:**
{json.dumps(context, indent=2)}

**SPECIFIC REQUIREMENTS:**
- For Note 10: Map 'Deposits (Asset)' to Security Deposits
- For Note 11: Map relevant accounts to Consumables
- For Note 12: Map receivables to Other Receivables (no aging data available)
- For Note 13: Map accounts to Bank Balances, Cash on Hand, Fixed Deposits
- For Note 14: Categorize into:
  - Unsecured, considered good:
    - Prepaid Expenses: Use value from 'Prepaid Expenses'
    - Other Advances: Use value from 'Loans & Advances (Asset)'
  - Other loans and advances:
    - Advance tax: Use value from 'TDS Advance Tax Paid SEC 100'
    - Balances with statutory/government authorities: Use value from 'Tds Receivables'
- For Note 15: Map to Interest Accrued
- Generate markdown_content for each note with the specified table format:
```
{markdown_content}
```

**CALCULATION RULES:**
- Use trial balance data for exact values
- Convert amounts to lakhs by dividing by 100000
- Round to 2 decimal places
- Validate totals: Sum of subcategories must equal the grand total
- Include generated_on timestamp: {datetime.now().isoformat()}
- Exclude inappropriate accounts for each note as specified

Generate the complete JSON structure now:
"""
        return prompt
    
    def call_openrouter_api(self, prompt: str) -> Optional[str]:
        """Make API call to OpenRouter with model fallback"""
        for model in self.recommended_models:
            print(f"🤖 Trying model: {model}")
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial reporting expert. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 8000,
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            try:
                response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=60)
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ Successful response from {model}")
                return content
            except (requests.exceptions.RequestException, KeyError, IndexError) as e:
                print(f"❌ Failed with {model}: {e}")
                continue
        
        print("❌ All models failed")
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
    
    def save_generated_note(self, note_data: str, note_number: str, output_dir: str = "generated_notes") -> bool:
        """Save the generated note to file in both JSON and markdown formats"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        json_output_path = f"{output_dir}/note_{note_number}.json"
        raw_output_path = f"{output_dir}/note_{note_number}_raw.txt"
        formatted_md_path = f"{output_dir}/note_{note_number}_formatted.md"
        
        try:
            with open(raw_output_path, 'w', encoding='utf-8') as f:
                f.write(note_data)
            print(f"💾 Raw response saved to {raw_output_path}")
            
            json_data, json_string = self.extract_json_from_markdown(note_data)
            if json_data:
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"✅ JSON saved to {json_output_path}")
                
                if 'markdown_content' in json_data:
                    with open(formatted_md_path, 'w', encoding='utf-8') as f:
                        f.write(json_data['markdown_content'])
                    print(f"📝 Formatted markdown saved to {formatted_md_path}")
                
                return True
            else:
                fallback_json = {
                    "note_number": note_number,
                    "raw_response": note_data,
                    "error": "Could not parse JSON from response",
                    "generated_on": datetime.now().isoformat()
                }
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(fallback_json, f, indent=2, ensure_ascii=False)
                print(f"⚠️ Fallback JSON saved to {json_output_path}")
                return False
        except Exception as e:
            print(f"❌ Error saving files: {e}")
            return False
    
    def generate_note(self, note_number: str, trial_balance_path: str = "output/parsed_trial_balance.json") -> bool:
        """Generate a specific note based on note number"""
        trial_balance_data = self.load_trial_balance(trial_balance_path)
        if not trial_balance_data:
            return False
        
        classified_accounts = self.classify_accounts_by_note(trial_balance_data, note_number)
        if not classified_accounts:
            print(f"❌ No accounts classified for Note {note_number}")
            return False
        
        prompt = self.build_llm_prompt(note_number, trial_balance_data, classified_accounts)
        if not prompt:
            print(f"❌ Failed to build prompt for Note {note_number}")
            return False
        
        response = self.call_openrouter_api(prompt)
        if not response:
            print(f"❌ Failed to get response from OpenRouter for Note {note_number}")
            return False
        
        return self.save_generated_note(response, note_number)
    
    def generate_all_notes(self, trial_balance_path: str = "output/parsed_trial_balance.json") -> bool:
        """Generate all notes defined in note_temp.py"""
        success = True
        for note_number in self.note_templates.keys():
            print(f"📄 Generating Note {note_number}: {self.note_templates[note_number]['title']}")
            if not self.generate_note(note_number, trial_balance_path):
                print(f"❌ Failed to generate Note {note_number}")
                success = False
        return success

if __name__ == "__main__":
    generator = FlexibleFinancialNoteGenerator()
    generator.generate_all_notes()