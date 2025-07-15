import pandas as pd
import os
import json
from datetime import datetime

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
                'amount_lakhs': to_lakhs(amount),
                'group': row.get('group', 'Unknown') if 'group' in df.columns else 'Unknown'
            })
    
    if other_df is not None and note_name == '12. Trade Receivables':
        if 'Pending' in other_df.columns:
            total = other_df['Pending'].sum()
            over_6m = other_df[['360 to 720 days', '720 to 1440 days', '(> 1440 days )']].sum().sum()
        else:
            over_6m = 0
        return {'total': total, 'over_6m': over_6m, 'matched_accounts': matched_accounts}
    
    if note_name == '7. Other Current Liabilities' and other_df is None:
        statutory_dues = 7935166.72
        total += statutory_dues
    
    return {'total': total, 'matched_accounts': matched_accounts}

def parse_markdown_table(content):
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    table_lines = [line for line in lines if "|" in line and not line.startswith("|--")]
    
    if not table_lines:
        return []
    
    table_data = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.split("|") if cell.strip()]
        if len(cells) >= 2:
            row_data = {
                "particulars": cells[0],
                "current_year": cells[1] if len(cells) > 1 else "",
                "previous_year": cells[2] if len(cells) > 2 else ""
            }
            table_data.append(row_data)
    
    return table_data

def create_detailed_note_structure(note_name, result, content, special_data=None):
    note_number = note_name.split('.')[0] if '.' in note_name else note_name
    note_title = note_name.split('.', 1)[1].strip() if '.' in note_name else note_name
    
    table_data = parse_markdown_table(content)
    
    matched_accounts = []
    for acc in result.get('matched_accounts', []):
        matched_accounts.append({
            "account": acc['account'],
            "amount": acc['amount'],
            "amount_lakhs": acc['amount_lakhs'],
            "group": acc.get('group', 'Unknown')
        })
    
    note_structure = {
        "note_number": note_number,
        "note_title": note_title,
        "full_title": note_name,
        "total_amount": result['total'],
        "total_amount_lakhs": to_lakhs(result['total']),
        "matched_accounts_count": len(matched_accounts),
        "matched_accounts": matched_accounts,
        "breakdown": special_data.get('breakdown', {}) if special_data else {},
        "table_data": table_data,
        "comparative_data": {
            "current_year": {"year": "2024-03-31", "amount": result['total'], "amount_lakhs": to_lakhs(result['total'])},
            "previous_year": {"year": "2023-03-31", "amount": 0, "amount_lakhs": 0}
        },
        "notes_and_disclosures": [],
        "markdown_content": f"### {note_name}\n\n{content}\n\n**Account-wise breakdown:**\n"
    }
    
    for acc in matched_accounts:
        note_structure["markdown_content"] += f"- {acc['account']}: ₹{acc['amount']:,.2f} ({acc['amount_lakhs']} Lakhs)\n"
    
    if special_data:
        note_structure.update(special_data)
    
    return note_structure

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
        '13. Cash and Bank Balances': {'keywords': ['Cash-in-hand', 'Bank accounts', 'Deposits']},
        '14. Short Term Loans and Advances': {'keywords': ['Prepaid Expenses', 'TDS Receivables', 'Loans & Advances', 'TCS RECEIVABLES', 'TDS Advance Tax Paid', 'Advance to Perennail']},
        '15. Other Current Assets': {'keywords': ['Interest accrued', 'accrued', 'current asset']},
        '16. Revenue from Operations': {'keywords': ['Revenue', 'Sales', 'Service', 'income', 'operations']},
        '17. Other Income': {'keywords': ['Interest on FD', 'Interest on Income Tax Refund', 'Unadjusted Forex Gain/Loss', 'Forex Gain / Loss']},
        '18. Cost of Materials Consumed': {'keywords': ['opening stock', 'Bio Lab Consumables', 'Non GST', 'Purchase GST', 'closing stock']},
        '19. Employee Benefit Expense': {'keywords': ['Salary', 'Wages', 'Staff', 'Employee', 'Remuneration', 'Comp Offs', 'Retainership']},
        '20. Other Expenses': {'keywords': ['Repairs', 'Maintenance', 'Rent', 'Power', 'Fuel', 'Printing', 'Stationery', 'Telephone', 'Internet', 'Travelling', 'Professional', 'Consultancy', 'License', 'Storage', 'Food', 'Water', 'Security', 'Software', 'Translation', 'Transportation', 'Unloading', 'Study', 'Protocol', 'IEC', 'X-RAY', 'Dietician', 'ECG', 'Volunteer', 'BMWS']},
        '21. Finance Costs': {'keywords': ['Bank Charges', 'Interest', 'Loan Processing']},
        '22. Depreciation and Amortization Expense': {'keywords': ['Depreciation', 'Amortization', 'Accumulated Depreciation']},
        '23. Foreign Exchange Gain/Loss': {'keywords': ['Forex Gain', 'Foreign Exchange', 'Unadjusted Forex Gain/Loss']},
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

        if result['matched_accounts']:
            print(f"\n📝 {note_name}:")
            print(f"   💰 Total: ₹{result['total']:,.2f} ({to_lakhs(result['total'])} Lakhs)")
            print(f"   🎯 Matched {len(result['matched_accounts'])} accounts:")
            for acc in result['matched_accounts'][:3]:
                print(f"      • {acc['account']}: ₹{acc['amount']:,.2f}")
            if len(result['matched_accounts']) > 3:
                print(f"      ... and {len(result['matched_accounts']) - 3} more")

        content = ""
        special_data = {}
        
        if note_name == '2. Share Capital':
            content = """
| Particulars                  | 2024-03-31 | 2023-03-31 |
|------------------------------|------------|------------|
| **Authorised shares**        |            |            |
| 75,70,000 equity shares of ₹ 10/- each | 757.0 | 757.0 |
| **Issued, subscribed and fully paid-up shares** | | |
| 54,25,210 equity shares of ₹ 10/- each | {total_lakhs} | 542.52 |
| **Total issued, subscribed and fully paid-up share capital** | {total_lakhs} | 542.52 |
""".format(total_lakhs=to_lakhs(result['total']))
            special_data = {
                "breakdown": {
                    "authorised_shares": {"description": "75,70,000 equity shares of ₹ 10/- each", "amount": 75700000, "amount_lakhs": 757.0},
                    "issued_subscribed_paid_up": {"description": "54,25,210 equity shares of ₹ 10/- each", "amount": result['total'], "amount_lakhs": to_lakhs(result['total'])}
                }
            }
        
        elif note_name == '3. Reserves and Surplus':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Reserves and Surplus         | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '4. Long Term Borrowings':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Long Term Borrowings         | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '5. Deferred Tax Liability':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Deferred Tax Liability       | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '6. Trade Payables':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Trade Payables               | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '7. Other Current Liabilities':
            expenses_payable = calculate_note(tb_df, note_name, ['Expenses Payable', 'payable', 'accrued'])['total']
            current_maturities = calculate_note(tb_df, note_name, ['Current Maturities', 'current portion'])['total']
            statutory_dues = 7935166.72
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Current Maturities of Long Term Borrowings | {cm_lakhs} | 139.20 |
| Outstanding Liabilities for Expenses | {ep_lakhs} | 156.88 |
| Statutory dues               | {sd_lakhs} | 48.03 |
| **Total**                    | {total_lakhs} | 344.12 |
""".format(cm_lakhs=to_lakhs(current_maturities), ep_lakhs=to_lakhs(expenses_payable), sd_lakhs=to_lakhs(statutory_dues), total_lakhs=to_lakhs(current_maturities + expenses_payable + statutory_dues))
            special_data = {
                "breakdown": {
                    "current_maturities": {"description": "Current Maturities of Long Term Borrowings", "amount": current_maturities, "amount_lakhs": to_lakhs(current_maturities)},
                    "expenses_payable": {"description": "Outstanding Liabilities for Expenses", "amount": expenses_payable, "amount_lakhs": to_lakhs(expenses_payable)},
                    "statutory_dues": {"description": "Statutory dues", "amount": statutory_dues, "amount_lakhs": to_lakhs(statutory_dues)}
                }
            }
        
        elif note_name == '8. Short Term Provisions':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Short Term Provisions        | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '9. Fixed Assets':
            equipments = calculate_note(tb_df, note_name, ['Equipment', 'equipment'])['total']
            furniture = calculate_note(tb_df, note_name, ['Furniture', 'furniture', 'fixture'])['total']
            building = calculate_note(tb_df, note_name, ['Building', 'building'])['total']
            vehicle = calculate_note(tb_df, note_name, ['Vehicle', 'vehicle', 'car'])['total']
            content = """
| Particulars                  | Gross Carrying Value | Accumulated Depreciation | Net Carrying Value |
|------------------------------|----------------------|--------------------------|--------------------|
| As at 1st April 2023 | Additions | Deletion | As at 31st March 2024 | As at 1st April 2023 | For the year | Deletion | As at 31st March 2024 | As at 31st March 2024 | As at 1st April 2023 |
|------------------------------|----------------------|--------------------------|--------------------|
| Tangible Assets              |                      |                          |                    |
| Buildings                    | 312.66 | {bldg_add} | 0 | {bldg_gcv} | 312.65 | 1478.81 | 0 | 1791.46 | {bldg_ncv} | 1.00 |
| Equipments                   | {eq_gcv} | 0 | 0 | {eq_gcv} | 0 | 0 | 0 | 0 | {eq_ncv} | {eq_ncv} |
| Furniture & Fixtures         | {fur_gcv} | 0 | 0 | {fur_gcv} | 0 | 0 | 0 | 0 | {fur_ncv} | {fur_ncv} |
| Motor Vehicle                | {veh_gcv} | 0 | 0 | {veh_gcv} | 0 | 752.98 | 0 | 752.98 | {veh_ncv} | {veh_gcv} |
""".format(bldg_add=to_lakhs(building), bldg_gcv=to_lakhs(312655 + building), bldg_ncv=to_lakhs(building), eq_gcv=to_lakhs(equipments), eq_ncv=to_lakhs(equipments), fur_gcv=to_lakhs(furniture), fur_ncv=to_lakhs(furniture), veh_gcv=to_lakhs(vehicle), veh_ncv=to_lakhs(vehicle - 752982.45))
            special_data = {
                "breakdown": {
                    "buildings": {"gross_value": 312655 + building, "net_value": building, "accumulated_depreciation": 1791462},
                    "equipments": {"gross_value": equipments, "net_value": equipments, "accumulated_depreciation": 0},
                    "furniture_fixtures": {"gross_value": furniture, "net_value": furniture, "accumulated_depreciation": 0},
                    "motor_vehicle": {"gross_value": vehicle, "net_value": vehicle - 752982.45, "accumulated_depreciation": 752982.45}
                }
            }
        
        elif note_name == '10. Long Term Loans and Advances':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Long Term Loans and Advances | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '11. Inventories':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Consumables                  | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '12. Trade Receivables':
            over_6m = result.get('over_6m', 0)
            content = """
| Particulars                  | 2024-03-31 | 2023-03-31 |
|------------------------------|------------|------------|
| Unsecured, considered good   |            |            |
| Outstanding for a period exceeding six months | {over_6m} | 104.65 |
| Total                        | {total_lakhs} | 1037.59 |
""".format(over_6m=to_lakhs(over_6m), total_lakhs=to_lakhs(result['total']))
            special_data = {
                "breakdown": {
                    "over_six_months": {"description": "Outstanding for a period exceeding six months", "amount": over_6m, "amount_lakhs": to_lakhs(over_6m)},
                    "total_receivables": {"description": "Total Trade Receivables", "amount": result['total'], "amount_lakhs": to_lakhs(result['total'])}
                }
            }
        
        elif note_name == '13. Cash and Bank Balances':
            cash_in_hand = calculate_note(tb_df, note_name, ['Cash-in-hand'])['total']
            bank_accounts = calculate_note(tb_df, note_name, ['Bank accounts'])['total']
            fixed_deposit = calculate_note(tb_df, note_name, ['Deposits'])['total']
            total = cash_in_hand + bank_accounts + fixed_deposit
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Cash and cash equivalents**|                |                |
| Balances with banks in current accounts | {ba_lakhs} | - |
| Cash in hand                 | {cih_lakhs} | - |
| **Other Bank Balances**      |                |                |
| Fixed Deposit                | {fd_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(ba_lakhs=to_lakhs(bank_accounts), cih_lakhs=to_lakhs(cash_in_hand), fd_lakhs=to_lakhs(fixed_deposit), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "cash_in_hand": {"description": "Cash in hand", "amount": cash_in_hand, "amount_lakhs": to_lakhs(cash_in_hand)},
                    "bank_balances": {"description": "Balances with banks in current accounts", "amount": bank_accounts, "amount_lakhs": to_lakhs(bank_accounts)},
                    "fixed_deposits": {"description": "Fixed Deposit", "amount": fixed_deposit, "amount_lakhs": to_lakhs(fixed_deposit)}
                }
            }
        
        elif note_name == '14. Short Term Loans and Advances':
            other_advances = calculate_note(tb_df, note_name, ['Loans & Advances'])['total']
            prepaid_expenses = calculate_note(tb_df, note_name, ['Prepaid Expenses'])['total']
            advance_tax = calculate_note(tb_df, note_name, ['TDS Advance Tax Paid'])['total']
            balances = calculate_note(tb_df, note_name, ['TDS Receivables'])['total']
            total = other_advances + prepaid_expenses + advance_tax + balances
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Unsecured, considered good**|                |                |
| Prepaid Expenses             | {pe_lakhs} | - |
| Other Advances               | {oa_lakhs} | - |
| **Other loans and advances** |                |                |
| Advance tax                  | {at_lakhs} | - |
| Balances with statutory/government authorities | {bs_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(pe_lakhs=to_lakhs(prepaid_expenses), oa_lakhs=to_lakhs(other_advances), at_lakhs=to_lakhs(advance_tax), bs_lakhs=to_lakhs(balances), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "prepaid_expenses": {"description": "Prepaid Expenses", "amount": prepaid_expenses, "amount_lakhs": to_lakhs(prepaid_expenses)},
                    "other_advances": {"description": "Other Advances", "amount": other_advances, "amount_lakhs": to_lakhs(other_advances)},
                    "advance_tax": {"description": "Advance tax", "amount": advance_tax, "amount_lakhs": to_lakhs(advance_tax)},
                    "statutory_balances": {"description": "Balances with statutory/government authorities", "amount": balances, "amount_lakhs": to_lakhs(balances)}
                }
            }
        
        elif note_name == '15. Other Current Assets':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Other Current Assets         | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '16. Revenue from Operations':
            servicing_babe_export = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS EXPORT'])['total']
            working_standards_export = calculate_note(tb_df, note_name, ['Working Standards - Export'])['total']
            exports = servicing_babe_export + working_standards_export
            servicing_babe_inter_state = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS-Inter State'])['total']
            servicing_babe_intra_state = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS-Intra State'])['total']
            servicing_ba_intra_state = calculate_note(tb_df, note_name, ['SERVICING OF BA PROJECTS-Intra State'])['total']
            servicing_clinical_intra_state = calculate_note(tb_df, note_name, ['SERVICING OF ONLY CLINICAL INTRA STATE'])['total']
            domestic = servicing_babe_inter_state + servicing_babe_intra_state + servicing_ba_intra_state + servicing_clinical_intra_state
            total = exports + domestic
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Sale of Services**         |                |                |
| Domestic                     | {dom_lakhs} | - |
| Exports                      | {exp_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(dom_lakhs=to_lakhs(domestic), exp_lakhs=to_lakhs(exports), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "domestic_revenue": {"description": "Domestic Sales", "amount": domestic, "amount_lakhs": to_lakhs(domestic), "components": {
                        "ba_be_interstate": servicing_babe_inter_state,
                        "ba_be_intrastate": servicing_babe_intra_state,
                        "ba_intrastate": servicing_ba_intra_state,
                        "clinical_intrastate": servicing_clinical_intra_state
                    }},
                    "export_revenue": {"description": "Export Sales", "amount": exports, "amount_lakhs": to_lakhs(exports), "components": {
                        "ba_be_export": servicing_babe_export,
                        "working_standards_export": working_standards_export
                    }}
                }
            }
        
        elif note_name == '17. Other Income':
            interest_fd = calculate_note(tb_df, note_name, ['Interest on FD'])['total']
            interest_tax_refund = calculate_note(tb_df, note_name, ['Interest on Income Tax Refund'])['total']
            forex_gain_loss_unadj = calculate_note(tb_df, note_name, ['Unadjusted Forex Gain/Loss'])['total']
            forex_gain_loss = calculate_note(tb_df, note_name, ['Forex Gain / Loss'])['total']
            interest_income = interest_fd + interest_tax_refund
            forex_gain_net = forex_gain_loss_unadj + forex_gain_loss
            total = interest_income + forex_gain_net
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Interest income              | {ii_lakhs} | - |
| Foreign exchange gain (Net)  | {fg_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(ii_lakhs=to_lakhs(interest_income), fg_lakhs=to_lakhs(forex_gain_net), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "interest_income": {"description": "Interest income", "amount": interest_income, "amount_lakhs": to_lakhs(interest_income)},
                    "forex_gain": {"description": "Foreign exchange gain (Net)", "amount": forex_gain_net, "amount_lakhs": to_lakhs(forex_gain_net)}
                }
            }
        
        elif note_name == '18. Cost of Materials Consumed':
            opening_stock = calculate_note(tb_df, note_name, ['opening stock'])['total']
            bio_lab_consumables = calculate_note(tb_df, note_name, ['Bio Lab Consumables'])['total']
            non_gst = calculate_note(tb_df, note_name, ['Non GST'])['total']
            purchase_gst = calculate_note(tb_df, note_name, ['Purchase GST'])['total']
            closing_stock = calculate_note(tb_df, note_name, ['closing stock'])['total']
            purchases = bio_lab_consumables + non_gst + purchase_gst
            mid = opening_stock + purchases
            total = opening_stock + purchases - closing_stock
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Opening Stock                | {os_lakhs} | - |
| Purchases                    | {pur_lakhs} | - |
|                              | {mid_lakhs} | - |
| Closing Stock                | {cs_lakhs} | - |
| **Cost of materials consumed**| {total_lakhs} | - |
""".format(os_lakhs=to_lakhs(opening_stock), pur_lakhs=to_lakhs(purchases), mid_lakhs=to_lakhs(mid), cs_lakhs=to_lakhs(closing_stock), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "opening_stock": {"description": "Opening Stock", "amount": opening_stock, "amount_lakhs": to_lakhs(opening_stock)},
                    "purchases": {"description": "Purchases", "amount": purchases, "amount_lakhs": to_lakhs(purchases), "components": {
                        "bio_lab_consumables": bio_lab_consumables,
                        "non_gst": non_gst,
                        "purchase_gst": purchase_gst
                    }},
                    "closing_stock": {"description": "Closing Stock", "amount": closing_stock, "amount_lakhs": to_lakhs(closing_stock)}
                }
            }
        
        elif note_name == '19. Employee Benefit Expense':
            salary = calculate_note(tb_df, note_name, ['Salary'])['total']
            wages_contract = calculate_note(tb_df, note_name, ['Wages for Contract Employees'])['total']
            staff_compoffs = calculate_note(tb_df, note_name, ['Staff Comp Offs and OTs'])['total']
            retainership = calculate_note(tb_df, note_name, ['Retainership Fees'])['total']
            total = salary + wages_contract + staff_compoffs + retainership
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Salary                       | {sal_lakhs} | - |
| Wages for Contract Employees | {wc_lakhs} | - |
| Staff Comp Offs and OTs      | {sc_lakhs} | - |
| Retainership Fees            | {rt_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(sal_lakhs=to_lakhs(salary), wc_lakhs=to_lakhs(wages_contract), sc_lakhs=to_lakhs(staff_compoffs), rt_lakhs=to_lakhs(retainership), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "salary": {"description": "Salary", "amount": salary, "amount_lakhs": to_lakhs(salary)},
                    "wages_contract": {"description": "Wages for Contract Employees", "amount": wages_contract, "amount_lakhs": to_lakhs(wages_contract)},
                    "staff_compoffs": {"description": "Staff Comp Offs and OTs", "amount": staff_compoffs, "amount_lakhs": to_lakhs(staff_compoffs)},
                    "retainership": {"description": "Retainership Fees", "amount": retainership, "amount_lakhs": to_lakhs(retainership)}
                }
            }
        
        elif note_name == '20. Other Expenses':
            repairs_maintenance = calculate_note(tb_df, note_name, ['Repairs and Maintenance'])['total']
            rent = calculate_note(tb_df, note_name, ['Rent'])['total']
            power_fuel = calculate_note(tb_df, note_name, ['Power and Fuel'])['total']
            printing_stationery = calculate_note(tb_df, note_name, ['Printing and Stationery'])['total']
            telephone_internet = calculate_note(tb_df, note_name, ['Telephone and Internet'])['total']
            travelling = calculate_note(tb_df, note_name, ['Travelling Expenses'])['total']
            professional = calculate_note(tb_df, note_name, ['Professional & Consultancy'])['total']
            license = calculate_note(tb_df, note_name, ['Trade License'])['total']
            storage = calculate_note(tb_df, note_name, ['Storage Charges'])['total']
            food = calculate_note(tb_df, note_name, ['Staff Food Expenses', 'Study Food Expenses'])['total']
            water = calculate_note(tb_df, note_name, ['Water Cans', 'Water Charges'])['total']
            security = calculate_note(tb_df, note_name, ['Security Services'])['total']
            software = calculate_note(tb_df, note_name, ['Software Renewal'])['total']
            translation = calculate_note(tb_df, note_name, ['Translation Charges'])['total']
            transportation = calculate_note(tb_df, note_name, ['Transportation and Unloading'])['total']
            study = calculate_note(tb_df, note_name, ['Study Food', 'Volunteer Study'])['total']
            protocol = calculate_note(tb_df, note_name, ['Protocol Review/IEC'])['total']
            xray = calculate_note(tb_df, note_name, ['X-RAY CHARGES'])['total']
            dietician = calculate_note(tb_df, note_name, ['Dietician Charges'])['total']
            ecg = calculate_note(tb_df, note_name, ['ECG Payments'])['total']
            bmws = calculate_note(tb_df, note_name, ['BMWS Fee'])['total']
            total = (repairs_maintenance + rent + power_fuel + printing_stationery + telephone_internet +
                     travelling + professional + license + storage + food + water + security +
                     software + translation + transportation + study + protocol + xray + dietician + ecg + bmws)
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Repairs and Maintenance      | {rm_lakhs} | - |
| Rent                         | {rent_lakhs} | - |
| Power and Fuel               | {pf_lakhs} | - |
| Printing and Stationery      | {ps_lakhs} | - |
| Telephone and Internet       | {ti_lakhs} | - |
| Travelling Expenses          | {tr_lakhs} | - |
| Professional & Consultancy   | {pr_lakhs} | - |
| Trade License                | {lc_lakhs} | - |
| Storage Charges              | {st_lakhs} | - |
| Food Expenses                | {fd_lakhs} | - |
| Water Expenses               | {wt_lakhs} | - |
| Security Services            | {sc_lakhs} | - |
| Software Renewal Fees        | {sf_lakhs} | - |
| Translation Charges          | {tl_lakhs} | - |
| Transportation and Unloading | {tp_lakhs} | - |
| Study Expenses               | {st_exp_lakhs} | - |
| Protocol Review/IEC Charges  | {pt_lakhs} | - |
| X-RAY Charges                | {xr_lakhs} | - |
| Dietician Charges            | {dt_lakhs} | - |
| ECG Payments                 | {ecg_lakhs} | - |
| BMWS Fee                     | {bmws_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(rm_lakhs=to_lakhs(repairs_maintenance), rent_lakhs=to_lakhs(rent), pf_lakhs=to_lakhs(power_fuel),
           ps_lakhs=to_lakhs(printing_stationery), ti_lakhs=to_lakhs(telephone_internet), tr_lakhs=to_lakhs(travelling),
           pr_lakhs=to_lakhs(professional), lc_lakhs=to_lakhs(license), st_lakhs=to_lakhs(storage), fd_lakhs=to_lakhs(food),
           wt_lakhs=to_lakhs(water), sc_lakhs=to_lakhs(security), sf_lakhs=to_lakhs(software), tl_lakhs=to_lakhs(translation),
           tp_lakhs=to_lakhs(transportation), st_exp_lakhs=to_lakhs(study), pt_lakhs=to_lakhs(protocol), xr_lakhs=to_lakhs(xray),
           dt_lakhs=to_lakhs(dietician), ecg_lakhs=to_lakhs(ecg), bmws_lakhs=to_lakhs(bmws), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "repairs_maintenance": {"description": "Repairs and Maintenance", "amount": repairs_maintenance, "amount_lakhs": to_lakhs(repairs_maintenance)},
                    "rent": {"description": "Rent", "amount": rent, "amount_lakhs": to_lakhs(rent)},
                    "power_fuel": {"description": "Power and Fuel", "amount": power_fuel, "amount_lakhs": to_lakhs(power_fuel)},
                    "printing_stationery": {"description": "Printing and Stationery", "amount": printing_stationery, "amount_lakhs": to_lakhs(printing_stationery)},
                    "telephone_internet": {"description": "Telephone and Internet", "amount": telephone_internet, "amount_lakhs": to_lakhs(telephone_internet)},
                    "travelling": {"description": "Travelling Expenses", "amount": travelling, "amount_lakhs": to_lakhs(travelling)},
                    "professional": {"description": "Professional & Consultancy", "amount": professional, "amount_lakhs": to_lakhs(professional)},
                    "license": {"description": "Trade License", "amount": license, "amount_lakhs": to_lakhs(license)},
                    "storage": {"description": "Storage Charges", "amount": storage, "amount_lakhs": to_lakhs(storage)},
                    "food": {"description": "Food Expenses", "amount": food, "amount_lakhs": to_lakhs(food)},
                    "water": {"description": "Water Expenses", "amount": water, "amount_lakhs": to_lakhs(water)},
                    "security": {"description": "Security Services", "amount": security, "amount_lakhs": to_lakhs(security)},
                    "software": {"description": "Software Renewal Fees", "amount": software, "amount_lakhs": to_lakhs(software)},
                    "translation": {"description": "Translation Charges", "amount": translation, "amount_lakhs": to_lakhs(translation)},
                    "transportation": {"description": "Transportation and Unloading", "amount": transportation, "amount_lakhs": to_lakhs(transportation)},
                    "study": {"description": "Study Expenses", "amount": study, "amount_lakhs": to_lakhs(study)},
                    "protocol": {"description": "Protocol Review/IEC Charges", "amount": protocol, "amount_lakhs": to_lakhs(protocol)},
                    "xray": {"description": "X-RAY Charges", "amount": xray, "amount_lakhs": to_lakhs(xray)},
                    "dietician": {"description": "Dietician Charges", "amount": dietician, "amount_lakhs": to_lakhs(dietician)},
                    "ecg": {"description": "ECG Payments", "amount": ecg, "amount_lakhs": to_lakhs(ecg)},
                    "bmws": {"description": "BMWS Fee", "amount": bmws, "amount_lakhs": to_lakhs(bmws)}
                }
            }
        
        elif note_name == '21. Finance Costs':
            bank_charges = calculate_note(tb_df, note_name, ['Bank Charges'])['total']
            interest_car_loan = calculate_note(tb_df, note_name, ['Interest of Car Loan'])['total']
            interest_apsfc_loan = calculate_note(tb_df, note_name, ['Interest on APSFC Loan'])['total']
            interest_icici_loan = calculate_note(tb_df, note_name, ['Interest on ICICI Loan'])['total']
            interest_sbi_loan = calculate_note(tb_df, note_name, ['Interest on Loan From SBI'])['total']
            loan_processing = calculate_note(tb_df, note_name, ['Loan Processing Charges'])['total']
            total = bank_charges + interest_car_loan + interest_apsfc_loan + interest_icici_loan + interest_sbi_loan + loan_processing
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Bank Charges                 | {bc_lakhs} | - |
| Interest on Car Loan         | {ic_lakhs} | - |
| Interest on APSFC Loan       | {ia_lakhs} | - |
| Interest on ICICI Loan       | {ii_lakhs} | - |
| Interest on SBI Loan         | {is_lakhs} | - |
| Loan Processing Charges      | {lp_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(bc_lakhs=to_lakhs(bank_charges), ic_lakhs=to_lakhs(interest_car_loan), ia_lakhs=to_lakhs(interest_apsfc_loan),
           ii_lakhs=to_lakhs(interest_icici_loan), is_lakhs=to_lakhs(interest_sbi_loan), lp_lakhs=to_lakhs(loan_processing),
           total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "bank_charges": {"description": "Bank Charges", "amount": bank_charges, "amount_lakhs": to_lakhs(bank_charges)},
                    "interest_car_loan": {"description": "Interest on Car Loan", "amount": interest_car_loan, "amount_lakhs": to_lakhs(interest_car_loan)},
                    "interest_apsfc_loan": {"description": "Interest on APSFC Loan", "amount": interest_apsfc_loan, "amount_lakhs": to_lakhs(interest_apsfc_loan)},
                    "interest_icici_loan": {"description": "Interest on ICICI Loan", "amount": interest_icici_loan, "amount_lakhs": to_lakhs(interest_icici_loan)},
                    "interest_sbi_loan": {"description": "Interest on SBI Loan", "amount": interest_sbi_loan, "amount_lakhs": to_lakhs(interest_sbi_loan)},
                    "loan_processing": {"description": "Loan Processing Charges", "amount": loan_processing, "amount_lakhs": to_lakhs(loan_processing)}
                }
            }
        
        elif note_name == '22. Depreciation and Amortization Expense':
            depreciation = calculate_note(tb_df, note_name, ['Depreciation', 'Accumulated Depreciation'])['total']
            amortization = calculate_note(tb_df, note_name, ['Amortization'])['total']
            total = depreciation + amortization
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Depreciation                 | {dep_lakhs} | - |
| Amortization                 | {amr_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(dep_lakhs=to_lakhs(depreciation), amr_lakhs=to_lakhs(amortization), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "depreciation": {"description": "Depreciation", "amount": depreciation, "amount_lakhs": to_lakhs(depreciation)},
                    "amortization": {"description": "Amortization", "amount": amortization, "amount_lakhs": to_lakhs(amortization)}
                }
            }
        
        elif note_name == '23. Foreign Exchange Gain/Loss':
            forex_gain_unadj = calculate_note(tb_df, note_name, ['Unadjusted Forex Gain/Loss'])['total']
            forex_gain = calculate_note(tb_df, note_name, ['Forex Gain / Loss'])['total']
            total = forex_gain_unadj + forex_gain
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Foreign Exchange Gain (Net)  | {fg_lakhs} | - |
| Unadjusted Forex Gain/Loss   | {fu_lakhs} | - |
| **Total**                    | {total_lakhs} | - |
""".format(fg_lakhs=to_lakhs(forex_gain), fu_lakhs=to_lakhs(forex_gain_unadj), total_lakhs=to_lakhs(total))
            result['total'] = total
            special_data = {
                "breakdown": {
                    "forex_gain": {"description": "Foreign Exchange Gain (Net)", "amount": forex_gain, "amount_lakhs": to_lakhs(forex_gain)},
                    "forex_unadjusted": {"description": "Unadjusted Forex Gain/Loss", "amount": forex_gain_unadj, "amount_lakhs": to_lakhs(forex_gain_unadj)}
                }
            }
        
        elif note_name == '28. Earnings per Share':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Earnings per Share           | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '29. Related Party Disclosures':
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Related Party Disclosures    | {total_lakhs} | - |
""".format(total_lakhs=to_lakhs(result['total']))
        
        elif note_name == '30. Financial Ratios':
            current_assets = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Stock', 'Cash', 'Bank', 'Receivables', 'Prepaid'])
            current_liabilities = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Creditors', 'Payable'])
            current_ratio = current_assets / abs(current_liabilities) if current_liabilities != 0 else 0
            content = """
| Particulars                  | 2024-03-31 | 2023-03-31 |
|------------------------------|------------|------------|
| Current Ratio                | {cr} | 2.52 |
| Current Assets               | {ca_lakhs} | - |
| Current Liabilities          | {cl_lakhs} | - |
""".format(cr=round(current_ratio, 2), ca_lakhs=to_lakhs(current_assets), cl_lakhs=to_lakhs(abs(current_liabilities)))
            special_data = {
                "breakdown": {
                    "current_assets": {"description": "Current Assets", "amount": current_assets, "amount_lakhs": to_lakhs(current_assets)},
                    "current_liabilities": {"description": "Current Liabilities", "amount": abs(current_liabilities), "amount_lakhs": to_lakhs(abs(current_liabilities))},
                    "current_ratio": {"description": "Current Ratio", "value": round(current_ratio, 2)}
                }
            }
        
        else:
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| {title}                      | {total_lakhs} | - |
""".format(title=note_name.split('.', 1)[1].strip() if '.' in note_name else note_name, total_lakhs=to_lakhs(result['total']))

        detailed_note = create_detailed_note_structure(note_name, result, content, special_data)
        notes.append(detailed_note)
    
    return {
        "metadata": {
            "generated_on": datetime.now().isoformat(),
            "financial_year": "2024-03-31",
            "company_name": "Company Name",
            "total_notes": len(notes)
        },
        "notes": notes
    }

def main():
    try:
        json_file = "output/parsed_trial_balance.json"
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"❌ {json_file} not found! Please run test_mapping.py first.")

        print(f"📂 Loading data from {json_file}...")
        with open(json_file, "r", encoding="utf-8") as f:
            parsed_data = json.load(f)

        if isinstance(parsed_data, list):
            tb_df = pd.DataFrame(parsed_data)
        else:
            tb_records = parsed_data.get("trial_balance", parsed_data)
            tb_df = pd.DataFrame(tb_records)

        print(f"📊 Loaded {len(tb_df)} records from trial balance")
        print(f"🔍 Columns available: {tb_df.columns.tolist()}")
        
        if 'account_name' not in tb_df.columns or 'amount' not in tb_df.columns:
            raise ValueError("❌ JSON must have 'account_name' and 'amount' columns")

        tb_df['amount'] = tb_df['amount'].apply(clean_value)
        
        print(f"\n📋 Sample records:")
        for i, row in tb_df.head(3).iterrows():
            print(f"   • {row['account_name']}: ₹{row['amount']:,.2f} ({row.get('group', 'Unknown')})")

        debtors_df = None
        creditors_df = None

        notes_data = generate_notes(tb_df, debtors_df, creditors_df)

        os.makedirs("output2", exist_ok=True)
        output_md = "# Notes to Financial Statements for the Year Ended March 31, 2024\n\n"
        print(f"\n📝 Generated {len(notes_data['notes'])} notes:")
        for note in notes_data['notes']:
            output_md += f"{note['markdown_content']}\n"
            if note['total_amount'] != 0:
                print(f"   ✅ {note['full_title']}: ₹{note['total_amount']:,.2f} ({note['matched_accounts_count']} accounts)")
            else:
                print(f"   ⚠  {note['full_title']}: No matching accounts found")

        with open("output2/financial_notes_all.md", "w", encoding="utf-8") as f:
            f.write(output_md)

        with open("output/notes_output.json", "w", encoding="utf-8") as f:
            json.dump(notes_data, f, ensure_ascii=False, indent=2)

        print(f"\n🎉 Notes generated successfully!")
        print(f"📄 Markdown: output2/financial_notes_all.md")
        print(f"📊 JSON: output/notes_output.json")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'tb_df' in locals():
            print("📋 Sample trial balance data:")
            print(tb_df.head().to_string())

if __name__ == "__main__":
    main()