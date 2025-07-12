




import pandas as pd
import json
import sys
import os
import re
import glob
from pathlib import Path
import requests
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

def load_mappings():
    exact_mappings = {}
    keyword_rules = {}
    if Path('config/mapping.json').exists():
        with open('config/mapping.json', 'r') as f:
            exact_mappings = json.load(f)
    if Path('config/rules.json').exists():
        with open('config/rules.json', 'r') as f:
            keyword_rules = json.load(f)
    return exact_mappings, keyword_rules

def get_smart_rules():
    return {
        'Cash and Cash Equivalents': [r'\b(cash|bank|petty|till|vault|fd|fixed\s*deposit)\b'],
        'Trade Receivables': [r'\b(debtor|receivable|customer|outstanding.*debtor)\b'],
        'Trade Payables': [r'\b(creditor|payable|supplier|vendor|outstanding.*creditor)\b'],
        'Inventories': [r'\b(stock|inventory|goods|raw\s*material|wip|work.*progress)\b'],
        'Property, Plant and Equipment': [r'\b(land|building|plant|machinery|equipment|furniture|vehicle|depreciation)\b'],
        'Equity Share Capital': [r'\b(capital|share.*capital|paid.*up|equity)\b'],
        'Revenue from Operations': [r'\b(sales?|revenue|turnover|service.*income)\b'],
        'Employee Benefits Expense': [r'\b(salary|wages?|staff|employee|pf|provident|gratuity)\b'],
        'Finance Costs': [r'\b(interest|finance.*cost|bank.*charge)\b'],
        'Other Current Liabilities': [r'\b(tds|gst|vat|tax.*payable|service.*tax)\b']
    }

def parse_amount(amount_str):
    if pd.isna(amount_str) or amount_str == '':
        return 0.0
    amount_str = str(amount_str).strip()
    is_credit = bool(re.search(r'\bcr\b', amount_str, re.IGNORECASE))
    is_debit = bool(re.search(r'\bdr\b', amount_str, re.IGNORECASE))
    amount_str = re.sub(r'[^\d\.\-\+]', '', amount_str)
    if not amount_str or amount_str in ['-', '+']:
        return 0.0
    try:
        amount = float(amount_str)
        if is_credit and amount > 0:
            amount = -amount
        return amount
    except ValueError:
        return 0.0

def classify_account(account_name, exact_mappings, keyword_rules, smart_rules):
    account_name_clean = account_name.strip().lower()
    
    # Prioritize exact match from mapping.json
    if account_name in exact_mappings:
        return exact_mappings[account_name], "mapping.json"
    for mapped_name, group in exact_mappings.items():
        if mapped_name.lower() == account_name_clean:
            return group, "mapping.json"
    
    # Check keyword rules from rules.json
    for group, keywords in keyword_rules.items():
        for keyword in keywords:
            if keyword.lower() in account_name_clean.split():
                return group, "rules.json"
    
    # Check smart rules with regex
    for group, patterns in smart_rules.items():
        for pattern in patterns:
            if re.search(pattern, account_name_clean):
                return group, "smart_rules"
    
    # Fallback to LLM if API key is available
    if api_key:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen/qwen3-30b-a3b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial expert. Classify the following account name into one of these categories: Equity, Non-Current Liability, Current Liability, Non-Current Asset, Current Asset, Revenue from Operations, Cost of Materials Consumed, Direct Expenses, Other Income, Other Expenses, Employee Benefits Expense, Finance Cost, Accumulated Depreciation, Deferred Tax Liability, Profit and Loss Account. Respond only with the category name."
                        },
                        {
                            "role": "user",
                            "content": account_name
                        }
                    ]
                }
            )
            llm_response = response.json()
            llm_suggestion = llm_response['choices'][0]['message']['content'].strip()
            return llm_suggestion, "llm_fallback"
        except Exception as e:
            print(f"LLM fallback failed: {e}")
            pass
    
    # Default to Unmapped if no match or LLM fails
    return 'Unmapped', 'Unmapped'

def extract_trial_balance_data(file_path):
    print(f"Parsing trial balance from: {file_path}")
    df_raw = pd.read_excel(file_path, header=None)
    print(f"Raw file: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
    exact_mappings, keyword_rules = load_mappings()
    smart_rules = get_smart_rules()
    print(f"Loaded {len(exact_mappings)} exact mappings, {len(keyword_rules)} keyword rules")
    structured_data = []
    source_file = Path(file_path).name
    for idx, row in df_raw.iterrows():
        account_name = row.iloc[0] if len(row) > 0 else None
        if pd.isna(account_name) or str(account_name).strip() == '':
            continue
        account_name = str(account_name).strip()
        if len(account_name) <= 2 or account_name.replace('.', '').replace('-', '').isdigit():
            continue
        amount = 0.0
        if len(row) > 3 and not pd.isna(row.iloc[3]):
            amount = parse_amount(row.iloc[3])
        elif len(row) > 2:
            debit = parse_amount(row.iloc[1]) if len(row) > 1 else 0.0
            credit = parse_amount(row.iloc[2]) if len(row) > 2 else 0.0
            amount = debit - credit
        group, mapped_by = classify_account(account_name, exact_mappings, keyword_rules, smart_rules)
        record = {
            "account_name": account_name,
            "group": group,
            "amount": amount,
            "mapped_by": mapped_by,
            "source_file": source_file
        }
        structured_data.append(record)
    return structured_data

def analyze_and_save_results(structured_data, output_file):
    total_records = len(structured_data)
    mapped_records = [r for r in structured_data if r['mapped_by'] != 'Unmapped']
    unmapped_records = [r for r in structured_data if r['mapped_by'] == 'Unmapped']
    success_rate = (len(mapped_records) / total_records * 100) if total_records > 0 else 0
    total_amount = sum(abs(r['amount']) for r in mapped_records)
    mapping_methods = {}
    for record in mapped_records:
        method = record['mapped_by']
        mapping_methods[method] = mapping_methods.get(method, 0) + 1
    account_groups = {}
    for record in mapped_records:
        group = record['group']
        if group not in account_groups:
            account_groups[group] = {'count': 0, 'total_amount': 0}
        account_groups[group]['count'] += 1
        account_groups[group]['total_amount'] += abs(record['amount'])
    os.makedirs('output', exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(structured_data, f, indent=2)
    print("\n" + "="*70)
    print("TRIAL BALANCE PARSING RESULTS")
    print("="*70)
    print(f"Total records processed: {total_records}")
    print(f"Successfully mapped: {len(mapped_records)}")
    print(f"Unmapped: {len(unmapped_records)}")
    print(f"Mapping success rate: {success_rate:.1f}%")
    print(f"Total mapped amount: ₹{total_amount:,.2f}")
    if mapping_methods:
        print(f"\nMAPPING METHODS USED:")
        for method, count in sorted(mapping_methods.items()):
            percentage = (count / len(mapped_records) * 100) if mapped_records else 0
            print(f"   {method}: {count} records ({percentage:.1f}%)")
    if account_groups:
        print(f"\nMAPPED ACCOUNT GROUPS:")
        for group, data in sorted(account_groups.items(), key=lambda x: x[1]['count'], reverse=True):
            percentage = (data['count'] / total_records * 100) if total_records > 0 else 0
            print(f"   {group}: {data['count']} records ({percentage:.1f}%) - ₹{data['total_amount']:,.2f}")
    if unmapped_records:
        print(f"\nUNMAPPED ACCOUNTS (showing first 10):")
        for i, record in enumerate(unmapped_records[:10], 1):
            amount_str = f"₹{abs(record['amount']):,.2f}" if record['amount'] != 0 else "₹0.00"
            print(f"   {i:2d}. {record['account_name']} - {amount_str}")
        if len(unmapped_records) > 10:
            print(f"   ... and {len(unmapped_records) - 10} more")
    print("\n" + "="*70)
    print("RECOMMENDATIONS:")
    if success_rate < 50:
        print("   Low mapping rate. Consider:")
        print("   • Adding more entries to mapping.json")
        print("   • Expanding keyword rules in rules.json")
        print("   • Standardizing account naming conventions")
    elif success_rate < 80:
        print("   Good mapping rate! Minor improvements:")
        print("   • Review unmapped accounts above")
        print("   • Add common patterns to rules")
    else:
        print("   Excellent mapping rate!")
        print("   • File is well-structured and ready for processing")
    print(f"\nResults saved to: {output_file}")
    print("="*70)
    return structured_data

def find_file(filename):
    possible_paths = [
        filename,
        f"input/{filename}",
        f"./{filename}",
    ]
    for path in possible_paths:
        if Path(path).exists():
            return path
    filename_lower = filename.lower()
    all_files = glob.glob("*.xlsx") + glob.glob("input/*.xlsx")
    for file_path in all_files:
        file_name_lower = Path(file_path).name.lower()
        if filename_lower in file_name_lower:
            return file_path
    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_mapping.py <excel_file>")
        print("Examples:")
        print("  python test_mapping.py 'Trial Balance.xlsx'")
        print("  python test_mapping.py Book2.xlsx")
        print("  python test_mapping.py Input.xlsx")
        sys.exit(1)
    filename = sys.argv[1]
    file_path = find_file(filename)
    if not file_path:
        print(f"File '{filename}' not found!")
        print("\nAvailable files:")
        excel_files = glob.glob("*.xlsx") + glob.glob("input/*.xlsx")
        for i, file in enumerate(excel_files, 1):
            print(f"   {i}. {file}")
        if not excel_files:
            print("   No Excel files found.")
        sys.exit(1)
    print(f"Found file: {file_path}")
    structured_data = extract_trial_balance_data(file_path)
    output_file = "output/parsed_trial_balance3.5.json"
    final_data = analyze_and_save_results(structured_data, output_file)
    if final_data:
        print(f"\nSAMPLE RECORD:")
        sample_record = final_data[0]
        print(json.dumps(sample_record, indent=2))
    print(f"\nProcessing complete! Check {output_file} for full results.")
