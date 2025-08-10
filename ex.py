import pandas as pd
import os
import json


def clean_value(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0

def to_lakhs(value):
    return round(value / 100000, 2)

def find_account_col(df):
    for col in df.columns:
        if df[col].astype(str).str.contains('account|particulars|name', case=False, na=False).any():
            return col
    return df.columns[0]

def find_balance_col(df):
    for col in df.columns:
        if df[col].dtype in [float, int] and df[col].notna().any():
            return col
    return df.columns[1] if len(df.columns) > 1 else None

def calculate_note(df, note_name, keywords, exclude=None, other_df=None):
    # Updated to work with the new DataFrame structure from test_mapping.py
    if 'account_name' in df.columns:
        account_col = 'account_name'
        balance_col = 'amount'
    else:
        account_col = find_account_col(df)
        balance_col = find_balance_col(df)
    
    if not balance_col:
        return {'total': 0}
    
    df = df.fillna(0)
    total = 0
    matched_accounts = []
    
    for idx, row in df.iterrows():
        account_name = str(row[account_col]).strip().lower()
        if any(kw.lower() in account_name for kw in keywords) and (not exclude or not any(ex.lower() in account_name for ex in exclude)):
            amount = clean_value(row[balance_col])
            total += amount
            matched_accounts.append({
                'account': str(row[account_col]),
                'amount': amount,
                'group': row.get('group', 'Unknown') if 'group' in df.columns else 'Unknown'
            })
    
    # Handle special cases
    if other_df is not None and note_name == '12. Trade Receivables':
        if 'Pending' in other_df.columns:
            total = other_df['Pending'].sum()
            over_6m = other_df[['360 to 720 days', '720 to 1440 days', '(> 1440 days )']].sum().sum()
        else:
            over_6m = 0
        return {'total': total, 'over_6m': over_6m, 'matched_accounts': matched_accounts}
    
    if note_name == '7. Other Current Liabilities' and other_df is None:
        statutory_dues = 7935166.72  # Static value
        total += statutory_dues
    
    return {'total': total, 'matched_accounts': matched_accounts}

def generate_notes(tb_df, debtors_df=None, creditors_df=None):
    notes = []
    note_mappings = {
        '2. Share Capital': {'keywords': ['Share Capital', 'share capital', 'equity share', 'paid up']},
        '3. Reserves and Surplus': {'keywords': ['Reserves', 'Surplus', 'reserves', 'surplus', 'retained earnings']},
        '4. Long Term Borrowings': {'keywords': ['loan', 'borrowing', 'term loan'], 'exclude': ['current maturities', 'short term']},
        '5. Deferred Tax Liability': {'keywords': ['Deferred Tax', 'deferred tax']},
        '6. Trade Payables': {'keywords': ['Creditors', 'creditors', 'trade payable', 'suppliers']},
        '7. Other Current Liabilities': {'keywords': ['Expenses Payable', 'Current Maturities', 'payable', 'accrued']},
        '8. Short Term Provisions': {'keywords': ['Provision', 'provision', 'taxation']},
        '9. Fixed Assets': {'keywords': ['Equipment', 'Furniture', 'Building', 'Vehicle', 'Motor', 'Asset', 'plant', 'machinery']},
        '10. Long Term Loans and Advances': {'keywords': ['Long Term', 'Security Deposits', 'advances', 'deposits']},
        '11. Inventories': {'keywords': ['Stock', 'Inventory', 'stock', 'inventory', 'goods']},
        '12. Trade Receivables': {'keywords': ['Receivables', 'receivables', 'debtors', 'trade receivable']},
        '13. Cash and Cash Equivalents': {'keywords': ['Cash', 'Bank', 'cash', 'bank', 'Fixed Deposit', 'fd']},
        '14. Short Term Loans and Advances': {'keywords': ['Prepaid', 'TDS', 'Advance', 'advance', 'prepaid']},
        '15. Other Current Assets': {'keywords': ['Interest accrued', 'accrued', 'current asset']},
        '16. Revenue from Operations': {'keywords': ['Revenue', 'Sales', 'Service', 'income', 'operations']},
        '17. Other Income': {'keywords': ['Interest income', 'other income', 'gain', 'forex']},
        '18. Cost of Materials Consumed': {'keywords': ['Purchase', 'Cost', 'Material', 'consumed']},
        '28. Earnings per Share': {'keywords': ['Profit', 'Loss', 'profit', 'loss']},
        '29. Related Party Disclosures': {'keywords': []},
        '30. Financial Ratios': {'keywords': ['Stock', 'Cash', 'Bank', 'Receivables', 'Creditors', 'Payable']}
    }

    print("🔍 Generating notes from parsed trial balance data...")
    print(f"📊 Total records in trial balance: {len(tb_df)}")
    
    for note_name, mapping in note_mappings.items():
        keywords = mapping['keywords']
        exclude = mapping.get('exclude', [])
        other_df = debtors_df if note_name == '12. Trade Receivables' else creditors_df if note_name == '6. Trade Payables' else None
        result = calculate_note(tb_df, note_name, keywords, exclude, other_df)

        # Print matching info for debugging
        if result['matched_accounts']:
            print(f"\n📝 {note_name}:")
            print(f"   💰 Total: ₹{result['total']:,.2f} ({to_lakhs(result['total'])} Lakhs)")
            print(f"   🎯 Matched {len(result['matched_accounts'])} accounts:")
            for acc in result['matched_accounts'][:3]:  # Show first 3
                print(f"      • {acc['account']}: ₹{acc['amount']:,.2f}")
            if len(result['matched_accounts']) > 3:
                print(f"      ... and {len(result['matched_accounts']) - 3} more")

        content = ""
        if note_name == '2. Share Capital':
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Authorised shares | | |
| 75,70,000 equity shares of ₹ 10/- each | {to_lakhs(75700000)} | {to_lakhs(75700000)} |
| Issued, subscribed and fully paid-up shares | | |
| 54,25,210 equity shares of ₹ 10/- each | {to_lakhs(result['total'])} | {to_lakhs(54252100)} |
| Total issued, subscribed and fully paid-up share capital | {to_lakhs(result['total'])} | {to_lakhs(54252100)} |
"""
        elif note_name == '7. Other Current Liabilities':
            expenses_payable = calculate_note(tb_df, note_name, ['Expenses Payable', 'payable', 'accrued'])['total']
            current_maturities = calculate_note(tb_df, note_name, ['Current Maturities', 'current portion'])['total']
            statutory_dues = 7935166.72  # Static value
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Current Maturities of Long Term Borrowings | {to_lakhs(current_maturities)} | {to_lakhs(13920441)} |
| Outstanding Liabilities for Expenses | {to_lakhs(expenses_payable)} | {to_lakhs(15688272)} |
| Statutory dues | {to_lakhs(statutory_dues)} | {to_lakhs(4803131.66)} |
| Total | {to_lakhs(current_maturities + expenses_payable + statutory_dues)} | {to_lakhs(34411844.66)} |
"""
        elif note_name == '9. Fixed Assets':
            equipments = calculate_note(tb_df, note_name, ['Equipment', 'equipment'])['total']
            furniture = calculate_note(tb_df, note_name, ['Furniture', 'furniture', 'fixture'])['total']
            building = calculate_note(tb_df, note_name, ['Building', 'building'])['total']
            vehicle = calculate_note(tb_df, note_name, ['Vehicle', 'vehicle', 'car'])['total']
            content = f"""
| Particulars | Gross Carrying Value | Accumulated Depreciation | Net Carrying Value |
|-------------|----------------------|--------------------------|--------------------|
| As at 1st April 2023 | Additions | Deletion | As at 31st March 2024 | As at 1st April 2023 | For the year | Deletion | As at 31st March 2024 | As at 31st March 2024 | As at 1st April 2023 |
| *Tangible Assets* | | | | | | | | | |
| Buildings | {to_lakhs(312655)} | {to_lakhs(building)} | 0 | {to_lakhs(312655 + building)} | {to_lakhs(312654)} | {to_lakhs(1478808)} | 0 | {to_lakhs(1791462)} | {to_lakhs(building)} | {to_lakhs(1)} |
| Equipments | {to_lakhs(equipments)} | {to_lakhs(0)} | 0 | {to_lakhs(equipments)} | {to_lakhs(0)} | {to_lakhs(0)} | 0 | {to_lakhs(0)} | {to_lakhs(equipments)} | {to_lakhs(equipments)} |
| Furniture & Fixtures | {to_lakhs(furniture)} | {to_lakhs(0)} | 0 | {to_lakhs(furniture)} | {to_lakhs(0)} | {to_lakhs(0)} | 0 | {to_lakhs(0)} | {to_lakhs(furniture)} | {to_lakhs(furniture)} |
| Motor Vehicle | {to_lakhs(vehicle)} | 0 | 0 | {to_lakhs(vehicle)} | {to_lakhs(0)} | {to_lakhs(752982.45)} | 0 | {to_lakhs(752982.45)} | {to_lakhs(vehicle - 752982.45)} | {to_lakhs(vehicle)} |
"""
        elif note_name == '12. Trade Receivables':
            over_6m = result.get('over_6m', 0)
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Unsecured, considered good | | |
| Outstanding for a period exceeding six months | {to_lakhs(over_6m)} | {to_lakhs(10465395)} |
| Total | {to_lakhs(result['total'])} | {to_lakhs(103758506)} |
"""
        elif note_name == '29. Related Party Disclosures':
            content = """
As per Accounting Standard 18, the disclosures of related parties as defined in the Accounting Standard are given below:
[Related party details require external input.]
"""
        elif note_name == '30. Financial Ratios':
            current_assets = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Stock', 'Cash', 'Bank', 'Receivables', 'Prepaid'])
            current_liabilities = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Creditors', 'Payable'])
            current_ratio = current_assets / abs(current_liabilities) if current_liabilities != 0 else 0
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Current Ratio | {round(current_ratio, 2)} | 2.52 |
| Current Assets | {to_lakhs(current_assets)} | - |
| Current Liabilities | {to_lakhs(abs(current_liabilities))} | - |
"""
        else:
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name} | {to_lakhs(result['total'])} | - |
"""
        notes.append({'Note': note_name, 'Content': content, 'Total': result['total'], 'Matched_Accounts': len(result.get('matched_accounts', []))})
    return notes

def main():
    try:
        # Load parsed_trial_balance.json from test_mapping.py output
        json_file = "output/parsed_trial_balance.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"❌ {json_file} not found! Please run test_mapping.py first.")

        print(f"📂 Loading data from {json_file}...")
        with open(json_file, "r", encoding="utf-8") as f:
            parsed_data = json.load(f)

        # Convert the list of records to DataFrame
        if isinstance(parsed_data, list):
            tb_df = pd.DataFrame(parsed_data)
        else:
            # Handle if it's wrapped in an object
            tb_records = parsed_data.get("trial_balance", parsed_data)
            tb_df = pd.DataFrame(tb_records)

        print(f"📊 Loaded {len(tb_df)} records from trial balance")
        print(f"🔍 Columns available: {tb_df.columns.tolist()}")
        
        # Ensure we have the required columns
        if 'account_name' not in tb_df.columns or 'amount' not in tb_df.columns:
            raise ValueError("❌ JSON must have 'account_name' and 'amount' columns")

        # Clean amount values
        tb_df['amount'] = tb_df['amount'].apply(clean_value)
        
        # Show sample data
        print(f"\n📋 Sample records:")
        for i, row in tb_df.head(3).iterrows():
            print(f"   • {row['account_name']}: ₹{row['amount']:,.2f} ({row.get('group', 'Unknown')})")

        # Generate notes (no debtors/creditors for now)
        debtors_df = None
        creditors_df = None

        notes = generate_notes(tb_df, debtors_df, creditors_df)

        # Save to markdown
        os.makedirs("outputs", exist_ok=True)
        output = "# Notes to Financial Statements for the Year Ended March 31, 2024\n\n"
        
        print(f"\n📝 Generated {len(notes)} notes:")
        for note in notes:
            output += f"## {note['Note']}\n{note['Content']}\n"
            if note['Total'] != 0:
                print(f"   ✅ {note['Note']}: ₹{note['Total']:,.2f} ({note['Matched_Accounts']} accounts)")
            else:
                print(f"   ⚠  {note['Note']}: No matching accounts found")
        
        with open("outputs/financial_notes_all.md", "w", encoding="utf-8") as f:
            f.write(output)

        # Save to CSV
        output_df = pd.DataFrame([
            [note['Note'], note['Content'], note['Total'], note['Matched_Accounts']] for note in notes
        ], columns=["Note", "Content", "Total_Amount", "Matched_Accounts"])
        
        output_df.to_csv("outputs/notes_output.csv", index=False, encoding="utf-8")
        
        print(f"\n🎉 Notes generated successfully!")
        print(f"📄 Markdown: outputs/financial_notes_all.md")
        print(f"📊 CSV: outputs/notes_output.csv")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'tb_df' in locals():
            print("📋 Sample trial balance data:")
            print(tb_df.head().to_string())

if _name_ == "_main_":
    main()
