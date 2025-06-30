#!/usr/bin/env python3

import pandas as pd
import json
import sys
from pathlib import Path
import re
import glob

def load_mappings():
    exact_mappings = {}
    keyword_rules = {}
    
    if Path('mapping.json').exists():
        with open('mapping.json', 'r') as f:
            exact_mappings = json.load(f)
    
    if Path('rules.json').exists():
        with open('rules.json', 'r') as f:
            keyword_rules = json.load(f)
    
    return exact_mappings, keyword_rules

def get_smart_rules():
    return {
        'Cash and Cash Equivalents': [r'cash|bank|petty|till|vault|fd|fixed\s*deposit'],
        'Trade Receivables': [r'debtor|receivable|customer|outstanding.*debtor'],
        'Trade Payables': [r'creditor|payable|supplier|vendor|outstanding.*creditor'],
        'Inventories': [r'stock|inventory|goods|raw\s*material|wip|work.*progress'],
        'Property, Plant and Equipment': [r'land|building|plant|machinery|equipment|furniture|vehicle|depreciation'],
        'Equity Share Capital': [r'capital|share.*capital|paid.*up|equity'],
        'Revenue from Operations': [r'sales?|revenue|turnover|service.*income'],
        'Employee Benefits Expense': [r'salary|wages?|staff|employee|pf|provident|gratuity'],
        'Finance Costs': [r'interest|finance.*cost|bank.*charge'],
        'Other Current Liabilities': [r'tds|gst|vat|tax.*payable|service.*tax']
    }

def classify_account(account_name, exact_mappings, keyword_rules, smart_rules):
    account_name_clean = account_name.strip().lower()
    
    if account_name in exact_mappings:
        return exact_mappings[account_name]
    
    for mapped_name, group in exact_mappings.items():
        if mapped_name.lower() == account_name_clean:
            return group
    
    for group, keywords in keyword_rules.items():
        for keyword in keywords:
            if keyword.lower() in account_name_clean:
                return group
    
    for group, patterns in smart_rules.items():
        for pattern in patterns:
            if re.search(pattern, account_name_clean):
                return group
    
    return 'Unmapped'

def test_mapping_from_excel(file_path):
    print(f" Analyzing file: {file_path}")
    
    df_raw = pd.read_excel(file_path, header=None)
    print(f" Raw file: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
    
    exact_mappings, keyword_rules = load_mappings()
    smart_rules = get_smart_rules()
    
    print(f" Loaded {len(exact_mappings)} exact mappings, {len(keyword_rules)} keyword rules")
    
    all_text_data = []
    for col in df_raw.columns:
        col_data = df_raw[col].dropna().astype(str)
        for value in col_data:
            value = value.strip()
            if len(value) > 2 and not value.replace('.', '').replace('-', '').isdigit():
                all_text_data.append(value)
    
    print(f" Found {len(all_text_data)} text entries to analyze")
    
    mapped_count = 0
    unmapped_count = 0
    mappings = {}
    unmapped_items = []
    
    for text_item in all_text_data:
        group = classify_account(text_item, exact_mappings, keyword_rules, smart_rules)
        if group != 'Unmapped':
            mapped_count += 1
            mappings[group] = mappings.get(group, 0) + 1
        else:
            unmapped_count += 1
            unmapped_items.append(text_item)
    
    total_items = len(all_text_data)
    success_rate = (mapped_count / total_items * 100) if total_items > 0 else 0
    
    print("\n" + "="*60)
    print(" MAPPING ANALYSIS RESULTS")
    print("="*60)
    print(f" Total text entries analyzed: {total_items}")
    print(f" Successfully mapped: {mapped_count}")
    print(f" Unmapped: {unmapped_count}")
    print(f" Mapping success rate: {success_rate:.1f}%")
    
    if mappings:
        print(f"\n MAPPED GROUPS:")
        for group, count in sorted(mappings.items()):
            percentage = (count / total_items * 100) if total_items > 0 else 0
            print(f"   {group}: {count} items ({percentage:.1f}%)")
    
    if unmapped_items:
        print(f"\n UNMAPPED ITEMS (showing first 10):")
        for i, item in enumerate(unmapped_items[:10], 1):
            print(f"   {i:2d}. {item}")
        if len(unmapped_items) > 10:
            print(f"   ... and {len(unmapped_items) - 10} more")
    
    print("\n" + "="*60)
    print("💡 RECOMMENDATION FOR COMPANY:")
    if success_rate < 50:
        print("   File structure is complex. Please provide:")
        print("   • Simple Excel with clear column headers")
        print("   • Columns: Account Name, Debit, Credit (or Amount)")
        print("   • Remove company headers and formatting")
    elif success_rate < 80:
        print("   Good mapping rate! Minor improvements needed:")
        print("   • Standardize account names")
        print("   • Check unmapped items above")
    else:
        print("   Excellent! File should work well once structure is fixed.")
    print("="*60)

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
        print(f" File '{filename}' not found!")
        print("\nAvailable files:")
        
        excel_files = glob.glob("*.xlsx") + glob.glob("input/*.xlsx")
        for i, file in enumerate(excel_files, 1):
            print(f"   {i}. {file}")
        
        if not excel_files:
            print("   No Excel files found.")
        sys.exit(1)
    
    print(f" Found file: {file_path}")
    test_mapping_from_excel(file_path)