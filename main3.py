import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class NotesToAccountsGenerator:
    def __init__(self, input_file: str = "output/parsed_trial_balance.json"):
        self.input_file = input_file
        self.output_dir = "output"
        self.financial_year = "2024-03-31"
        self.previous_year = "2023-03-31"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def clean_value(self, value: Any) -> float:
        """Clean and convert value to float"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def to_lakhs(self, value: float) -> float:
        """Convert amount to lakhs"""
        return round(value / 100000, 2)
    
    def load_trial_balance(self) -> List[Dict[str, Any]]:
        """Load trial balance data from JSON file"""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"❌ {self.input_file} not found!")
        
        print(f"📂 Loading data from {self.input_file}...")
        with open(self.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            tb_data = data
        elif isinstance(data, dict):
            tb_data = data.get("trial_balance", data.get("data", []))
        else:
            raise ValueError("❌ Invalid JSON structure")
        
        print(f"📊 Loaded {len(tb_data)} records from trial balance")
        return tb_data
    
    def filter_accounts_by_group(self, tb_data: List[Dict[str, Any]], target_group: str) -> List[Dict[str, Any]]:
        """Filter accounts by group"""
        filtered_accounts = []
        
        for account in tb_data:
            # Clean the amount
            account['amount'] = self.clean_value(account.get('amount', 0))
            
            # Check if account belongs to target group
            account_group = account.get('group', '').strip()
            if target_group.lower() in account_group.lower():
                filtered_accounts.append(account)
        
        print(f"🔍 Found {len(filtered_accounts)} accounts in group '{target_group}'")
        return filtered_accounts
    
    def generate_note_structure(self, note_config: Dict[str, Any], filtered_accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate the complete note structure"""
        
        # Calculate totals
        total_amount = sum(acc['amount'] for acc in filtered_accounts)
        total_amount_lakhs = self.to_lakhs(total_amount)
        
        # Build matched accounts
        matched_accounts = []
        for account in filtered_accounts:
            if account['amount'] != 0:  # Only include non-zero accounts
                matched_accounts.append({
                    "account": account['account_name'],
                    "amount": account['amount'],
                    "amount_lakhs": self.to_lakhs(account['amount']),
                    "group": account.get('group', 'Unknown')
                })
        
        # Generate breakdown based on note type
        breakdown = self.generate_breakdown(note_config, filtered_accounts)
        
        # Generate table data
        table_data = self.generate_table_data(note_config, breakdown, total_amount_lakhs)
        
        # Generate markdown content
        markdown_content = self.generate_markdown_content(note_config, table_data, matched_accounts)
        
        # Build the complete note structure
        note_structure = {
            "note_number": note_config['note_number'],
            "note_title": note_config['note_title'],
            "full_title": f"{note_config['note_number']}. {note_config['note_title']}",
            "total_amount": total_amount,
            "total_amount_lakhs": total_amount_lakhs,
            "matched_accounts_count": len(matched_accounts),
            "matched_accounts": matched_accounts,
            "breakdown": breakdown,
            "table_data": table_data,
            "comparative_data": {
                "current_year": {
                    "year": self.financial_year,
                    "amount": total_amount,
                    "amount_lakhs": total_amount_lakhs
                },
                "previous_year": {
                    "year": self.previous_year,
                    "amount": 0,
                    "amount_lakhs": 0
                }
            },
            "notes_and_disclosures": [],
            "markdown_content": markdown_content
        }
        
        return note_structure
    
    def generate_breakdown(self, note_config: Dict[str, Any], filtered_accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate breakdown based on note type and account classification"""
        breakdown = {}
        
        # Get breakdown rules from note config
        breakdown_rules = note_config.get('breakdown_rules', {})
        
        if not breakdown_rules:
            # Default breakdown - group by account type
            breakdown["total"] = {
                "description": note_config['note_title'],
                "amount": sum(acc['amount'] for acc in filtered_accounts),
                "amount_lakhs": self.to_lakhs(sum(acc['amount'] for acc in filtered_accounts))
            }
            return breakdown
        
        # Apply custom breakdown rules
        for rule_key, rule_config in breakdown_rules.items():
            keywords = rule_config.get('keywords', [])
            description = rule_config.get('description', rule_key.replace('_', ' ').title())
            
            matching_accounts = []
            for account in filtered_accounts:
                account_name = account['account_name'].lower()
                if any(keyword.lower() in account_name for keyword in keywords):
                    matching_accounts.append(account)
            
            if matching_accounts:
                total_amount = sum(acc['amount'] for acc in matching_accounts)
                breakdown[rule_key] = {
                    "description": description,
                    "amount": total_amount,
                    "amount_lakhs": self.to_lakhs(total_amount)
                }
        
        return breakdown
    
    def generate_table_data(self, note_config: Dict[str, Any], breakdown: Dict[str, Any], total_lakhs: float) -> List[Dict[str, Any]]:
        """Generate table data for the note"""
        table_data = []
        
        # Add breakdown items to table
        for key, item in breakdown.items():
            if key != "total":
                table_data.append({
                    "particulars": item["description"],
                    "current_year": item["amount_lakhs"],
                    "previous_year": 0  # Default to 0 for previous year
                })
        
        # Add total row if there are multiple breakdown items
        if len(breakdown) > 1:
            table_data.append({
                "particulars": "**Total**",
                "current_year": total_lakhs,
                "previous_year": 0
            })
        
        return table_data
    
    def generate_markdown_content(self, note_config: Dict[str, Any], table_data: List[Dict[str, Any]], matched_accounts: List[Dict[str, Any]]) -> str:
        """Generate markdown content for the note"""
        note_title = f"{note_config['note_number']}. {note_config['note_title']}"
        
        markdown = f"### {note_title}\n\n"
        
        # Add table
        if table_data:
            markdown += "| Particulars | March 31, 2024 | March 31, 2023 |\n"
            markdown += "|-------------|----------------|----------------|\n"
            
            for row in table_data:
                particulars = row['particulars']
                current_year = row['current_year']
                previous_year = row['previous_year']
                markdown += f"| {particulars} | {current_year} | {previous_year} |\n"
        
        # Add account-wise breakdown
        if matched_accounts:
            markdown += "\n**Account-wise breakdown:**\n"
            for account in matched_accounts:
                markdown += f"- {account['account']}: ₹{account['amount']:,.2f} ({account['amount_lakhs']} Lakhs)\n"
        
        return markdown
    
    def generate_note(self, target_group: str, note_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete note for the specified group"""
        print(f"\n🎯 Generating note for group: {target_group}")
        
        # Load trial balance data
        tb_data = self.load_trial_balance()
        
        # Filter accounts by group
        filtered_accounts = self.filter_accounts_by_group(tb_data, target_group)
        
        if not filtered_accounts:
            print(f"⚠️  No accounts found for group '{target_group}'")
            return {}
        
        # Generate note structure
        note_structure = self.generate_note_structure(note_config, filtered_accounts)
        
        print(f"✅ Generated note: {note_structure['full_title']}")
        print(f"💰 Total Amount: ₹{note_structure['total_amount']:,.2f} ({note_structure['total_amount_lakhs']} Lakhs)")
        print(f"📊 Matched Accounts: {note_structure['matched_accounts_count']}")
        
        return note_structure
    
    def save_note(self, note_data: Dict[str, Any], filename: str = "note_output3.json"):
        """Save the generated note to a JSON file"""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(note_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Note saved to: {output_path}")
        return output_path

def main():
    """Main function to demonstrate the Notes to Accounts generator"""
    
    # Initialize the generator
    generator = NotesToAccountsGenerator()
    
    # Configuration for the note - you can modify this as needed
    TARGET_GROUP = "Current Liability"  # 🎯 Change this to filter different groups
    
    # Note configuration with breakdown rules
    note_config = {
        "note_number": "7",
        "note_title": "Other Current Liabilities",
        "breakdown_rules": {
            "current_maturities": {
                "description": "Current Maturities of Long Term Borrowings",
                "keywords": ["current maturities", "current portion", "maturity"]
            },
            "expenses_payable": {
                "description": "Outstanding Liabilities for Expenses",
                "keywords": ["expenses payable", "payable", "accrued expenses"]
            },
            "statutory_dues": {
                "description": "Statutory dues",
                "keywords": ["statutory", "tax payable", "dues", "government"]
            }
        }
    }
    
    try:
        # Generate the note
        note_data = generator.generate_note(TARGET_GROUP, note_config)
        
        if note_data:
            # Save the note
            output_path = generator.save_note(note_data)
            
            # Display summary
            print(f"\n🎉 Note generation completed successfully!")
            print(f"📄 Output saved to: {output_path}")
            
            # Show a preview of the generated note
            print(f"\n📋 Preview:")
            print(f"Title: {note_data['full_title']}")
            print(f"Total Amount: ₹{note_data['total_amount']:,.2f}")
            print(f"Accounts Matched: {note_data['matched_accounts_count']}")
            
            # Show breakdown
            if note_data['breakdown']:
                print(f"\n📊 Breakdown:")
                for key, item in note_data['breakdown'].items():
                    print(f"  • {item['description']}: ₹{item['amount']:,.2f} ({item['amount_lakhs']} Lakhs)")
        else:
            print("❌ No note generated - check if the target group has matching accounts")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()