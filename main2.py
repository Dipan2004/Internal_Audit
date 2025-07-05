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

def calculate_note(tb_df, note_num, note_title, keywords, exclude=None, special_breakdown=None):
    tb_df = tb_df.copy()
    tb_df['amount'] = tb_df['amount'].apply(clean_value)
    total = 0.0
    matched_accounts = []

    for idx, row in tb_df.iterrows():
        account_name = str(row['account_name']).strip().lower()
        if any(kw.lower() in account_name for kw in keywords) and (not exclude or not any(ex.lower() in account_name for ex in exclude)):
            amount = row['amount']
            total += amount
            matched_accounts.append({
                'account': row['account_name'],
                'amount': amount,
                'group': row.get('group', 'Unknown')
            })

    # Handle special breakdowns
    breakdown = {}
    if special_breakdown:
        for category, sub_keywords in special_breakdown.items():
            sub_total = sum(row['amount'] for idx, row in tb_df.iterrows() 
                           if any(kw.lower() in str(row['account_name']).strip().lower() for kw in sub_keywords))
            breakdown[category] = sub_total

    result = {'total': total, 'matched_accounts': matched_accounts}
    if breakdown:
        result['breakdown'] = breakdown
    return result

def calculate_subgroup_totals(tb_df, subgroups):
    subgroup_totals = {}
    if subgroups:  # Check if subgroups is not None and not empty
        for sub_name, sub_keywords in subgroups.items():
            sub_total = sum(row['amount'] for idx, row in tb_df.iterrows() 
                           if any(kw.lower() in str(row['account_name']).strip().lower() for kw in sub_keywords))
            subgroup_totals[sub_name] = sub_total
    return subgroup_totals

def generate_notes(tb_df):
    notes = []
    note_mappings = {
        '3. Reserves and Surplus': {
            'keywords': ['reserves', 'surplus', 'retained earnings'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Reserves and Surplus       | {total_lakhs} | - |
|   - Reserves & Surplus     | {reserves_lakhs} | - |
""",
            'subgroups': {
                'Reserves & Surplus': ['reserves', 'surplus']
            }
        },
        '5. Deferred Tax Liability': {
            'keywords': ['deferred tax', 'deferred tax liability'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Deferred Tax Liability     | {total_lakhs} | - |
"""
        },
        '10. Long Term Loans and Advances': {
            'keywords': ['long term', 'security deposits', 'advances', 'deposits'],
            'exclude': ['short term', 'prepaid'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Long Term Loans and Advances | {total_lakhs} | - |
|   - Deposits (Asset)       | {deposits_lakhs} | - |
""",
            'subgroups': {
                'Deposits (Asset)': ['deposits']
            }
        },
        '11. Inventories': {
            'keywords': ['stock', 'inventory', 'opening stock'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Inventories                | {total_lakhs} | - |
|   - Opening Stock          | {opening_stock_lakhs} | - |
""",
            'subgroups': {
                'Opening Stock': ['opening stock']
            }
        },
        '13. Cash and Cash Equivalents': {
            'keywords': ['cash', 'bank', 'fixed deposit', 'fd'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Cash and Cash Equivalents  | {total_lakhs} | - |
|   - Cash-in-Hand           | {cash_lakhs} | - |
|   - Bank Accounts          | {bank_lakhs} | - |
""",
            'subgroups': {
                'Cash-in-Hand': ['cash'],
                'Bank Accounts': ['bank']
            }
        },
        '16. Revenue from Operations': {
            'keywords': ['revenue', 'sales', 'service', 'operations'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Revenue from Operations    | {total_lakhs} | - |
|   - Sales Accounts         | {sales_lakhs} | - |
|   - Servicing of Projects  | {service_lakhs} | - |
""",
            'subgroups': {
                'Sales Accounts': ['sales'],
                'Servicing of Projects': ['service', 'projects']
            }
        },
        '17. Other Income': {
            'keywords': ['interest income', 'other income', 'gain', 'forex'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Other Income               | {total_lakhs} | - |
|   - Interest on FD         | {other_income_interest_lakhs} | - |
|   - Forex Gain / Loss      | {other_income_forex_lakhs} | - |
""",
            'subgroups': {
                'Interest on FD': ['interest'],
                'Forex Gain / Loss': ['forex']
            }
        },
        '18. Cost of Materials Consumed': {
            'keywords': ['purchase', 'cost', 'material', 'consumed'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Cost of Materials Consumed | {total_lakhs} | - |
|   - Purchase Accounts      | {purchase_lakhs} | - |
|   - Bio Lab Consumables    | {consumables_lakhs} | - |
""",
            'subgroups': {
                'Purchase Accounts': ['purchase'],
                'Bio Lab Consumables': ['consumables']
            }
        },
        '20. Payment to Auditors': {
            'keywords': ['audit', 'professional', 'consultancy'],
            'special_breakdown': {
                'Audit Fee': ['audit', 'audit fee'],
                'Tax Audit/Certification Fees': ['tax audit', 'certification', 'compliance']
            },
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Payment to Auditors        | {total_lakhs} | - |
|   - Audit Fee              | {audit_fee_lakhs} | - |
|   - Tax Audit / Certification Fees | {tax_audit_lakhs} | - |
"""
        },
        '21. Cost of Services Rendered': {
            'keywords': ['direct expenses', 'service charges', 'consultancy charges'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Cost of Services Rendered  | {total_lakhs} | - |
|   - Direct Expenses        | {direct_lakhs} | - |
|   - Ambulance Service Charges | {ambulance_lakhs} | - |
""",
            'subgroups': {
                'Direct Expenses': ['direct'],
                'Ambulance Service Charges': ['ambulance']
            }
        },
        '22. Employee Benefits Expense': {
            'keywords': ['salary', 'wages', 'employee', 'staff', 'gratuity', 'remuneration'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Employee Benefits Expense  | {total_lakhs} | - |
|   - Salary                 | {employee_salary_lakhs} | - |
|   - Remuneration to Directors | {employee_remuneration_lakhs} | - |
""",
            'subgroups': {
                'Salary': ['salary'],
                'Remuneration to Directors': ['remuneration']
            }
        },
        '23. Finance Costs': {
            'keywords': ['interest', 'finance cost', 'bank charge'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Finance Costs              | {total_lakhs} | - |
|   - Interest on Loans      | {finance_interest_lakhs} | - |
""",
            'subgroups': {
                'Interest on Loans': ['interest']
            }
        },
        '24. Depreciation and Amortization Expense': {
            'keywords': ['depreciation', 'amortization'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Depreciation and Amortization Expense | {total_lakhs} | - |
|   - Accumulated Depreciation | {depreciation_lakhs} | - |
""",
            'subgroups': {
                'Accumulated Depreciation': ['depreciation']
            }
        },
        '25. Other Expenses': {
            'keywords': ['indirect expenses', 'office expenses', 'rent', 'repairs'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Other Expenses             | {total_lakhs} | - |
|   - Rent of the Premises   | {other_rent_lakhs} | - |
|   - Electricity Charges    | {other_electricity_lakhs} | - |
""",
            'subgroups': {
                'Rent of the Premises': ['rent'],
                'Electricity Charges': ['electricity']
            }
        },
        '26. Earnings Per Share (EPS)': {
            'keywords': ['profit', 'loss', 'earnings'],
            'content_template': """
| Particulars                | 2024-03-31 | 2023-03-31 |
|----------------------------|------------|------------|
| Earnings Per Share (EPS)   | {total_lakhs} | - |
"""
        }
    }

    print("🔍 Generating notes from parsed trial balance data...")
    print(f"📊 Total records in trial balance: {len(tb_df)}")

    for note_title, mapping in note_mappings.items():
        if not note_title.startswith(tuple(str(i) for i in [3, 5, 10, 11, 13, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26])):
            continue
        
        result = calculate_note(tb_df, note_title, mapping['keywords'], mapping.get('exclude'), mapping.get('special_breakdown'))
        total = result['total']
        matched_accounts_count = len(result.get('matched_accounts', []))
        breakdown = result.get('breakdown', {})
        
        # Fix: Ensure subgroups is always a dictionary
        subgroups = mapping.get('subgroups', {})
        if subgroups is None:
            subgroups = {}

        # Calculate subgroup totals
        subgroup_totals = calculate_subgroup_totals(tb_df, subgroups)

        # Prepare content with dynamic values
        content = mapping['content_template'].format(
            total_lakhs=to_lakhs(total),
            reserves_lakhs=to_lakhs(subgroup_totals.get('Reserves & Surplus', 0)),
            deposits_lakhs=to_lakhs(subgroup_totals.get('Deposits (Asset)', 0)),
            opening_stock_lakhs=to_lakhs(subgroup_totals.get('Opening Stock', 0)),
            cash_lakhs=to_lakhs(subgroup_totals.get('Cash-in-Hand', 0)),
            bank_lakhs=to_lakhs(subgroup_totals.get('Bank Accounts', 0)),
            sales_lakhs=to_lakhs(subgroup_totals.get('Sales Accounts', 0)),
            service_lakhs=to_lakhs(subgroup_totals.get('Servicing of Projects', 0)),
            other_income_interest_lakhs=to_lakhs(subgroup_totals.get('Interest on FD', 0)),
            other_income_forex_lakhs=to_lakhs(subgroup_totals.get('Forex Gain / Loss', 0)),
            purchase_lakhs=to_lakhs(subgroup_totals.get('Purchase Accounts', 0)),
            consumables_lakhs=to_lakhs(subgroup_totals.get('Bio Lab Consumables', 0)),
            audit_fee_lakhs=to_lakhs(breakdown.get('Audit Fee', 0)),
            tax_audit_lakhs=to_lakhs(breakdown.get('Tax Audit/Certification Fees', 0)),
            direct_lakhs=to_lakhs(subgroup_totals.get('Direct Expenses', 0)),
            ambulance_lakhs=to_lakhs(subgroup_totals.get('Ambulance Service Charges', 0)),
            employee_salary_lakhs=to_lakhs(subgroup_totals.get('Salary', 0)),
            employee_remuneration_lakhs=to_lakhs(subgroup_totals.get('Remuneration to Directors', 0)),
            finance_interest_lakhs=to_lakhs(subgroup_totals.get('Interest on Loans', 0)),
            depreciation_lakhs=to_lakhs(subgroup_totals.get('Accumulated Depreciation', 0)),
            other_rent_lakhs=to_lakhs(subgroup_totals.get('Rent of the Premises', 0)),
            other_electricity_lakhs=to_lakhs(subgroup_totals.get('Electricity Charges', 0))
        )

        notes.append({
            'Note': note_title,
            'Content': content,
            'Total_Amount': total,
            'Matched_Accounts': matched_accounts_count
        })
        print(f"📝 {note_title}: ₹{total:,.2f} ({matched_accounts_count} accounts)")

    return notes

def main():
    try:
        json_file = "output/parsed_trial_balance.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"❌ {json_file} not found! Please run test_mapping.py first.")

        print(f"📂 Loading data from {json_file}...")
        with open(json_file, "r", encoding="utf-8") as f:
            parsed_data = json.load(f)

        tb_df = pd.DataFrame(parsed_data) if isinstance(parsed_data, list) else pd.DataFrame(parsed_data.get("trial_balance", parsed_data))

        print(f"📊 Loaded {len(tb_df)} records from trial balance")
        print(f"🔍 Columns available: {tb_df.columns.tolist()}")

        if 'account_name' not in tb_df.columns or 'amount' not in tb_df.columns:
            raise ValueError("❌ JSON must have 'account_name' and 'amount' columns")

        notes = generate_notes(tb_df)

        # Save to Markdown
        os.makedirs("outputs", exist_ok=True)
        output_md = "# Notes to Financial Statements for the Year Ended March 31, 2024\n\n"
        for note in notes:
            output_md += f"## {note['Note']}\n{note['Content']}\n"
        
        with open("outputs/financial_notes_all.md", "w", encoding="utf-8") as f:
            f.write(output_md)

        # Save to JSON
        with open("outputs/notes_output.json", "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

        print(f"\n🎉 Notes generated successfully!")
        print(f"📄 Markdown: outputs/financial_notes_all.md")
        print(f"📊 JSON: outputs/notes_output.json")

        # Verify Excel compatibility
        notes_df = pd.DataFrame(notes)
        print("\n📋 Sample DataFrame for Excel conversion:")
        print(notes_df.head().to_string())

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'tb_df' in locals():
            print("📋 Sample trial balance data:")
            print(tb_df.head().to_string())

if __name__ == "__main__":
    main()