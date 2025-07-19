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

def calculate_note(df, note_name, keywords, exclude=None):
    if 'account_name' in df.columns:
        account_col = 'account_name'
        balance_col = 'amount'
    else:
        account_col = find_account_col(df)
        balance_col = find_balance_col(df)
    
    if not balance_col:
        return {'total': 0, 'matched_accounts': []}
    
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
            "amount_lakhs": to_lakhs(acc['amount']),
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

def generate_notes(tb_df):
    notes = []
    note_mappings = {
        '16. Revenue from Operations': {
            'keywords': ['Revenue', 'Sales', 'Service', 'Income', 'Consultancy', 'Gain / Loss on Sales of Fixed Assets', 'Income Tax',
                         'Servicing of BA/BE PROJECTS', 'Working Standards - Export', 'SERVICING OF BA PROJECTS', 'SERVICING OF ONLY CLINICAL']
        },
        '17. Other Income': {
            'keywords': ['Interest on FD', 'Interest on Income Tax Refund', 'Unadjusted Forex Gain/Loss', 'Forex Gain / Loss', 'Interest']
        },
        '18. Cost of Materials Consumed': {
            'keywords': ['Opening Stock', 'Bio Lab Consumables', 'Non GST', 'Purchase GST', 'Closing Stock']
        },
        '19. Employee Benefit Expense': {
            'keywords': ['Salary', 'Wages', 'Bonus', 'Employee', 'Remuneration', 'Comp Offs', 'Retainership', 
                         'Employees Group Life Insurance', 'Employees Health & Personal Accident Insurance', 
                         'Prepaid - Employees Group Life Insurance', 'Prepaid Insurance - Employees Health & Personal Accident', 
                         'Staff Welfare Expenses', 'Employees Expenses Reimbursement', 'Contribution to PF', 'Contribution to ESI']
        },
        '20. Other Expenses': {
            'keywords': ['BA / BE NOC', 'BA Expenses', 'Payments to Volunteers', 'Other Operating Expenses', 'Laboratory testing', 
                         'Rent', 'Rates & Taxes', 'Fees & licenses', 'Insurance', 'Membership & Subscription', 
                         'Postage & Communication', 'Printing and Stationery', 'CSR Fund', 'Telephone & Internet', 
                         'Travelling and Conveyance', 'Translation Charges', 'Electricity Charges', 'Security Charges', 
                         'Annual Maintenance', 'Repairs and maintenance', 'Business Development', 'Professional & Consultancy', 
                         'Payment to Auditors', 'Bad Debts', 'Fire Extinguishers', 'Food Expenses', 'Diesel Expenses', 
                         'Interest Under 234 C', 'Loan Processing Charges', 'Sitting Fee of Directors', 'Customs Duty', 
                         'Transportation and Unloading', 'Software Equipment', 'Miscellaneous expenses', 'Laptop Accessories', 
                         'Professional Fee', 'Office Rent', 'Security Deposit']
        },
        '21. Depreciation and Amortisation Expense': {
            'keywords': ['Depreciation', 'Amortization', 'Accumulated Depreciation', 'Depreciation And Amortisation']
        },
        '22. Loss on Sale of Assets & Investments': {
            'keywords': ['Short Term Loss', 'Long term loss', 'Loss on Sale of Fixed Assets', 'Loss on Sale of Investments']
        },
        '23. Finance Costs': {
            'keywords': ['Bank Charges', 'Finance Charges', 'Interest', 'Loan Processing', 'Interest and penalty', 'Interest on TDS']
        },
        '24. Payment to Auditor': {
            'keywords': ['Payment to Auditors', 'Audit Fee', 'Tax Audit', 'Certification Fees']
        },
        '25. Earnings in Foreign Currency': {
            'keywords': ['Income from export of services', 'Servicing of BA/BE PROJECTS EXPORT', 'Working Standards - Export']
        },
        '26. Particulars of Un-hedged Foreign Currency Exposure': {
            'keywords': ['Income from export of services', 'Servicing of BA/BE PROJECTS EXPORT', 'Working Standards - Export']
        }
    }

    print("🔍 Generating notes 16-26 from parsed trial balance data...")
    print(f"📊 Total records in trial balance: {len(tb_df)}")
    
    for note_name, mapping in note_mappings.items():
        keywords = mapping['keywords']
        result = calculate_note(tb_df, note_name, keywords)

        if result['matched_accounts']:
            print(f"\n📝 {note_name}:")
            print(f"   💰 Total: ₹{result['total']:,.2f} ({to_lakhs(result['total'])} Lakhs)")
            print(f"   🎯 Matched {len(result['matched_accounts'])} accounts:")
            for acc in result['matched_accounts'][:3]:
                print(f"      • {acc['account']}: ₹{acc['amount']:,.2f}")
            if len(result['matched_accounts']) > 3:
                print(f"      ... and {len(result['matched_accounts']) - 3} more")
        else:
            print(f"\n📝 {note_name}: No matching accounts found")

        content = ""
        special_data = {}
        
        if note_name == '16. Revenue from Operations':
            servicing_babe_export = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS EXPORT'])['total']
            working_standards_export = calculate_note(tb_df, note_name, ['Working Standards - Export'])['total']
            exports = servicing_babe_export + working_standards_export
            servicing_babe_inter_state = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS-Inter State'])['total']
            servicing_babe_intra_state = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS-Intra State'])['total']
            servicing_ba_intra_state = calculate_note(tb_df, note_name, ['SERVICING OF BA PROJECTS-Intra State'])['total']
            servicing_clinical_intra_state = calculate_note(tb_df, note_name, ['SERVICING OF ONLY CLINICAL INTRA STATE'])['total']
            domestic = servicing_babe_inter_state + servicing_babe_intra_state + servicing_ba_intra_state + servicing_clinical_intra_state
            sales_other = calculate_note(tb_df, note_name, ['Sales', 'Gain / Loss on Sales of Fixed Assets', 'Consultancy & Service Fee', 'Income', 'Income Tax'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Sale of Services**         |                |                |
| Domestic                     | {dom_lakhs}    | -              |
| Exports                      | {exp_lakhs}    | -              |
| Sales and Other Income       | {sales_lakhs}  | -              |
| **Total**                    | {total_lakhs}  | -              |
""".format(dom_lakhs=to_lakhs(domestic), exp_lakhs=to_lakhs(exports), sales_lakhs=to_lakhs(sales_other), total_lakhs=to_lakhs(total))
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
                    }},
                    "sales_and_other": {"description": "Sales and Other Income", "amount": sales_other, "amount_lakhs": to_lakhs(sales_other)}
                }
            }
        
        elif note_name == '17. Other Income':
            interest_income = calculate_note(tb_df, note_name, ['Interest on FD', 'Interest on Income Tax Refund', 'Interest'])['total']
            forex_gain = calculate_note(tb_df, note_name, ['Unadjusted Forex Gain/Loss', 'Forex Gain / Loss'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Interest income              | {ii_lakhs}     | -              |
| Foreign exchange gain (Net)  | {fg_lakhs}     | -              |
| **Total**                    | {total_lakhs}  | -              |
""".format(ii_lakhs=to_lakhs(interest_income), fg_lakhs=to_lakhs(forex_gain), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "interest_income": {"description": "Interest income", "amount": interest_income, "amount_lakhs": to_lakhs(interest_income)},
                    "forex_gain": {"description": "Foreign exchange gain (Net)", "amount": forex_gain, "amount_lakhs": to_lakhs(forex_gain)}
                }
            }
        
        elif note_name == '18. Cost of Materials Consumed':
            opening_stock = calculate_note(tb_df, note_name, ['Opening Stock'])['total']
            purchases = calculate_note(tb_df, note_name, ['Bio Lab Consumables', 'Non GST', 'Purchase GST'])['total']
            closing_stock = calculate_note(tb_df, note_name, ['Closing Stock'])['total']
            total = opening_stock + purchases - closing_stock  # As per note structure
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Opening Stock                | {os_lakhs}     | -              |
| Add: Purchases               | {pur_lakhs}    | -              |
|                              | {subtotal_lakhs}| -             |
| Less: Closing Stock          | {cs_lakhs}     | -              |
| Cost of materials consumed   | {total_lakhs}  | -              |
""".format(os_lakhs=to_lakhs(opening_stock), pur_lakhs=to_lakhs(purchases), subtotal_lakhs=to_lakhs(opening_stock + purchases), 
           cs_lakhs=to_lakhs(closing_stock), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "opening_stock": {"description": "Opening Stock", "amount": opening_stock, "amount_lakhs": to_lakhs(opening_stock)},
                    "purchases": {"description": "Purchases", "amount": purchases, "amount_lakhs": to_lakhs(purchases)},
                    "closing_stock": {"description": "Closing Stock", "amount": closing_stock, "amount_lakhs": to_lakhs(closing_stock)},
                    "cost_consumed": {"description": "Cost of materials consumed", "amount": total, "amount_lakhs": to_lakhs(total)}
                }
            }
        
        elif note_name == '19. Employee Benefit Expense':
            salaries_wages_bonus = calculate_note(tb_df, note_name, ['Salary', 'Wages', 'Bonus', 'Remuneration', 'Comp Offs', 'Retainership'])['total']
            pf_esi = calculate_note(tb_df, note_name, ['Contribution to PF', 'Contribution to ESI'])['total']
            staff_welfare = calculate_note(tb_df, note_name, ['Staff Welfare Expenses', 'Employees Expenses Reimbursement'])['total']
            insurance = calculate_note(tb_df, note_name, ['Employees Group Life Insurance', 'Employees Health & Personal Accident Insurance', 
                                                         'Prepaid - Employees Group Life Insurance', 'Prepaid Insurance - Employees Health & Personal Accident'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Salaries, wages and bonus    | {swb_lakhs}    | -              |
| Contribution to PF & ESI     | {pf_esi_lakhs} | -              |
| Staff welfare expenses       | {sw_lakhs}     | -              |
| 
| **Total**                    | {total_lakhs}  | -              |
""".format(swb_lakhs=to_lakhs(salaries_wages_bonus), pf_esi_lakhs=to_lakhs(pf_esi), sw_lakhs=to_lakhs(staff_welfare), 
           ins_lakhs=to_lakhs(insurance), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "salaries_wages_bonus": {"description": "Salaries, wages and bonus", "amount": salaries_wages_bonus, "amount_lakhs": to_lakhs(salaries_wages_bonus)},
                    "pf_esi": {"description": "Contribution to PF & ESI", "amount": pf_esi, "amount_lakhs": to_lakhs(pf_esi)},
                    "staff_welfare": {"description": "Staff welfare expenses", "amount": staff_welfare, "amount_lakhs": to_lakhs(staff_welfare)},
                    "insurance": {"description": "Insurance Expenses", "amount": insurance, "amount_lakhs": to_lakhs(insurance)}
                }
            }
        
        elif note_name == '20. Other Expenses':
            ba_be_noc = calculate_note(tb_df, note_name, ['BA / BE NOC Charges'])['total']
            ba_expenses = calculate_note(tb_df, note_name, ['BA Expenses'])['total']
            volunteers = calculate_note(tb_df, note_name, ['Payments to Volunteers'])['total']
            other_operating = calculate_note(tb_df, note_name, ['Other Operating Expenses'])['total']
            lab_testing = calculate_note(tb_df, note_name, ['Laboratory testing charges'])['total']
            rent = calculate_note(tb_df, note_name, ['Rent', 'Office Rent'])['total']
            rates_taxes = calculate_note(tb_df, note_name, ['Rates & Taxes'])['total']
            fees_licenses = calculate_note(tb_df, note_name, ['Fees & licenses'])['total']
            insurance = calculate_note(tb_df, note_name, ['Insurance'])['total']
            membership = calculate_note(tb_df, note_name, ['Membership & Subscription Charges'])['total']
            postage = calculate_note(tb_df, note_name, ['Postage & Communication Cost'])['total']
            printing = calculate_note(tb_df, note_name, ['Printing and Stationery'])['total']
            csr = calculate_note(tb_df, note_name, ['CSR Fund Expenses'])['total']
            telephone = calculate_note(tb_df, note_name, ['Telephone & Internet', 'Telephone Expense'])['total']
            travelling = calculate_note(tb_df, note_name, ['Travelling and Conveyance'])['total']
            translation = calculate_note(tb_df, note_name, ['Translation Charges'])['total']
            electricity = calculate_note(tb_df, note_name, ['Electricity Charges'])['total']
            security = calculate_note(tb_df, note_name, ['Security Charges', 'Security Deposit', 'Security Deposit - ESIC', 
                                                        'Security Deposits - Awfis Space Solutions Private Limited', 
                                                        'Security Deposits - Concept Classic Converge', 'Security Deposit - Hive Space'])['total']
            maintenance = calculate_note(tb_df, note_name, ['Annual Maintenance Charges', 'Laptop Accessories and Maintenance', 
                                                           'Laptop Annual Maintenance Charges'])['total']
            repairs_electrical = calculate_note(tb_df, note_name, ['Repairs and maintenance - Electrical'])['total']
            repairs_office = calculate_note(tb_df, note_name, ['Repairs and maintenance - Office'])['total']
            repairs_machinery = calculate_note(tb_df, note_name, ['Repairs and maintenance - Machinery'])['total']
            repairs_vehicles = calculate_note(tb_df, note_name, ['Repairs and maintenance - Vehicles'])['total']
            repairs_others = calculate_note(tb_df, note_name, ['Repairs and maintenance - Others'])['total']
            business_dev = calculate_note(tb_df, note_name, ['Business Development Expenses'])['total']
            professional = calculate_note(tb_df, note_name, ['Professional & Consultancy', 'Professional Fee', 
                                                            'Provision for Professional Fee', 'Professional Fee (Transfer Pricing)'])['total']
            auditors = calculate_note(tb_df, note_name, ['Payment to Auditors'])['total']
            bad_debts = calculate_note(tb_df, note_name, ['Bad Debts Written Off'])['total']
            fire_extinguishers = calculate_note(tb_df, note_name, ['Fire Extinguishers Refilling Charges'])['total']
            food_guests = calculate_note(tb_df, note_name, ['Food Expenses for Guests'])['total']
            diesel = calculate_note(tb_df, note_name, ['Diesel Expenses'])['total']
            interest_234c = calculate_note(tb_df, note_name, ['Interest Under 234 C'])['total']
            loan_processing = calculate_note(tb_df, note_name, ['Loan Processing Charges'])['total']
            sitting_fee = calculate_note(tb_df, note_name, ['Sitting Fee of Directors'])['total']
            customs_duty = calculate_note(tb_df, note_name, ['Customs Duty Payment'])['total']
            transportation = calculate_note(tb_df, note_name, ['Transportation and Unloading Charges'])['total']
            software = calculate_note(tb_df, note_name, ['Software Equipment'])['total']
            misc = calculate_note(tb_df, note_name, ['Miscellaneous expenses'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| BA / BE NOC Charges          | {ba_be_noc_lakhs} | -           |
| BA Expenses                  | {ba_exp_lakhs} | -             |
| Payments to Volunteers       | {vol_lakhs}    | -             |
| Other Operating Expenses     | {oo_lakhs}     | -             |
| Laboratory testing charges   | {lab_lakhs}    | -             |
| Rent                         | {rent_lakhs}   | -             |
| Rates & Taxes                | {rt_lakhs}     | -             |
| Fees & licenses              | {fl_lakhs}     | -             |
| Insurance                    | {ins_lakhs}    | -             |
| Membership & Subscription Charges | {mem_lakhs}| -             |
| Postage & Communication Cost | {post_lakhs}   | -             |
| Printing and stationery      | {print_lakhs}  | -             |
| CSR Fund Expenses            | {csr_lakhs}    | -             |
| Telephone & Internet         | {tel_lakhs}    | -             |
| Travelling and Conveyance    | {trav_lakhs}   | -             |
| Translation Charges          | {tl_lakhs}     | -             |
| Electricity Charges          | {elec_lakhs}   | -             |
| Security Charges             | {sec_lakhs}    | -             |
| Annual Maintenance Charges   | {maint_lakhs}  | -             |
| Repairs and maintenance      |                |                |
| - Electrical                 | {relec_lakhs}  | -             |
| - Office                     | {roff_lakhs}   | -             |
| - Machinery                  | {rmach_lakhs}  | -             |
| - Vehicles                   | {rveh_lakhs}   | -             |
| - Others                     | {roth_lakhs}   | -             |
| Business Development Expenses| {bd_lakhs}     | -             |
| Professional & Consultancy Fees | {prof_lakhs}| -             |
| Payment to Auditors          | {aud_lakhs}    | -             |
| Bad Debts Written Off        | {bd_debts_lakhs}| -            |
| Fire Extinguishers Refilling Charges | {fire_lakhs} | -          |
| Food Expenses for Guests     | {food_lakhs}   | -             |
| Diesel Expenses              | {diesel_lakhs} | -             |
| Interest Under 234 C Fy 2021-22 | {int234c_lakhs} | -         |
| Loan Processing Charges      | {loan_lakhs}   | -             |
| Sitting Fee of Directors     | {sit_lakhs}    | -             |
| Customs Duty Payment         | {cust_lakhs}   | -             |
| Transportation and Unloading Charges | {trans_lakhs} | -        |
| Software Equipment           | {soft_lakhs}   | -             |
| Miscellaneous expenses       | {misc_lakhs}   | -             |
| **Total**                    | {total_lakhs}  | -             |
""".format(ba_be_noc_lakhs=to_lakhs(ba_be_noc), ba_exp_lakhs=to_lakhs(ba_expenses), vol_lakhs=to_lakhs(volunteers), 
           oo_lakhs=to_lakhs(other_operating), lab_lakhs=to_lakhs(lab_testing), rent_lakhs=to_lakhs(rent), 
           rt_lakhs=to_lakhs(rates_taxes), fl_lakhs=to_lakhs(fees_licenses), ins_lakhs=to_lakhs(insurance), 
           mem_lakhs=to_lakhs(membership), post_lakhs=to_lakhs(postage), print_lakhs=to_lakhs(printing), 
           csr_lakhs=to_lakhs(csr), tel_lakhs=to_lakhs(telephone), trav_lakhs=to_lakhs(travelling), 
           tl_lakhs=to_lakhs(translation), elec_lakhs=to_lakhs(electricity), sec_lakhs=to_lakhs(security), 
           maint_lakhs=to_lakhs(maintenance), relec_lakhs=to_lakhs(repairs_electrical), roff_lakhs=to_lakhs(repairs_office), 
           rmach_lakhs=to_lakhs(repairs_machinery), rveh_lakhs=to_lakhs(repairs_vehicles), roth_lakhs=to_lakhs(repairs_others), 
           bd_lakhs=to_lakhs(business_dev), prof_lakhs=to_lakhs(professional), aud_lakhs=to_lakhs(auditors), 
           bd_debts_lakhs=to_lakhs(bad_debts), fire_lakhs=to_lakhs(fire_extinguishers), food_lakhs=to_lakhs(food_guests), 
           diesel_lakhs=to_lakhs(diesel), int234c_lakhs=to_lakhs(interest_234c), loan_lakhs=to_lakhs(loan_processing), 
           sit_lakhs=to_lakhs(sitting_fee), cust_lakhs=to_lakhs(customs_duty), trans_lakhs=to_lakhs(transportation), 
           soft_lakhs=to_lakhs(software), misc_lakhs=to_lakhs(misc), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "ba_be_noc": {"description": "BA / BE NOC Charges", "amount": ba_be_noc, "amount_lakhs": to_lakhs(ba_be_noc)},
                    "ba_expenses": {"description": "BA Expenses", "amount": ba_expenses, "amount_lakhs": to_lakhs(ba_expenses)},
                    "volunteers": {"description": "Payments to Volunteers", "amount": volunteers, "amount_lakhs": to_lakhs(volunteers)},
                    "other_operating": {"description": "Other Operating Expenses", "amount": other_operating, "amount_lakhs": to_lakhs(other_operating)},
                    "lab_testing": {"description": "Laboratory testing charges", "amount": lab_testing, "amount_lakhs": to_lakhs(lab_testing)},
                    "rent": {"description": "Rent", "amount": rent, "amount_lakhs": to_lakhs(rent)},
                    "rates_taxes": {"description": "Rates & Taxes", "amount": rates_taxes, "amount_lakhs": to_lakhs(rates_taxes)},
                    "fees_licenses": {"description": "Fees & licenses", "amount": fees_licenses, "amount_lakhs": to_lakhs(fees_licenses)},
                    "insurance": {"description": "Insurance", "amount": insurance, "amount_lakhs": to_lakhs(insurance)},
                    "membership": {"description": "Membership & Subscription Charges", "amount": membership, "amount_lakhs": to_lakhs(membership)},
                    "postage": {"description": "Postage & Communication Cost", "amount": postage, "amount_lakhs": to_lakhs(postage)},
                    "printing": {"description": "Printing and stationery", "amount": printing, "amount_lakhs": to_lakhs(printing)},
                    "csr": {"description": "CSR Fund Expenses", "amount": csr, "amount_lakhs": to_lakhs(csr)},
                    "telephone": {"description": "Telephone & Internet", "amount": telephone, "amount_lakhs": to_lakhs(telephone)},
                    "travelling": {"description": "Travelling and Conveyance", "amount": travelling, "amount_lakhs": to_lakhs(travelling)},
                    "translation": {"description": "Translation Charges", "amount": translation, "amount_lakhs": to_lakhs(translation)},
                    "electricity": {"description": "Electricity Charges", "amount": electricity, "amount_lakhs": to_lakhs(electricity)},
                    "security": {"description": "Security Charges", "amount": security, "amount_lakhs": to_lakhs(security)},
                    "maintenance": {"description": "Annual Maintenance Charges", "amount": maintenance, "amount_lakhs": to_lakhs(maintenance)},
                    "repairs_electrical": {"description": "Repairs and maintenance - Electrical", "amount": repairs_electrical, "amount_lakhs": to_lakhs(repairs_electrical)},
                    "repairs_office": {"description": "Repairs and maintenance - Office", "amount": repairs_office, "amount_lakhs": to_lakhs(repairs_office)},
                    "repairs_machinery": {"description": "Repairs and maintenance - Machinery", "amount": repairs_machinery, "amount_lakhs": to_lakhs(repairs_machinery)},
                    "repairs_vehicles": {"description": "Repairs and maintenance - Vehicles", "amount": repairs_vehicles, "amount_lakhs": to_lakhs(repairs_vehicles)},
                    "repairs_others": {"description": "Repairs and maintenance - Others", "amount": repairs_others, "amount_lakhs": to_lakhs(repairs_others)},
                    "business_dev": {"description": "Business Development Expenses", "amount": business_dev, "amount_lakhs": to_lakhs(business_dev)},
                    "professional": {"description": "Professional & Consultancy Fees", "amount": professional, "amount_lakhs": to_lakhs(professional)},
                    "auditors": {"description": "Payment to Auditors", "amount": auditors, "amount_lakhs": to_lakhs(auditors)},
                    "bad_debts": {"description": "Bad Debts Written Off", "amount": bad_debts, "amount_lakhs": to_lakhs(bad_debts)},
                    "fire_extinguishers": {"description": "Fire Extinguishers Refilling Charges", "amount": fire_extinguishers, "amount_lakhs": to_lakhs(fire_extinguishers)},
                    "food_guests": {"description": "Food Expenses for Guests", "amount": food_guests, "amount_lakhs": to_lakhs(food_guests)},
                    "diesel": {"description": "Diesel Expenses", "amount": diesel, "amount_lakhs": to_lakhs(diesel)},
                    "interest_234c": {"description": "Interest Under 234 C Fy 2021-22", "amount": interest_234c, "amount_lakhs": to_lakhs(interest_234c)},
                    "loan_processing": {"description": "Loan Processing Charges", "amount": loan_processing, "amount_lakhs": to_lakhs(loan_processing)},
                    "sitting_fee": {"description": "Sitting Fee of Directors", "amount": sitting_fee, "amount_lakhs": to_lakhs(sitting_fee)},
                    "customs_duty": {"description": "Customs Duty Payment", "amount": customs_duty, "amount_lakhs": to_lakhs(customs_duty)},
                    "transportation": {"description": "Transportation and Unloading Charges", "amount": transportation, "amount_lakhs": to_lakhs(transportation)},
                    "software": {"description": "Software Equipment", "amount": software, "amount_lakhs": to_lakhs(software)},
                    "misc": {"description": "Miscellaneous expenses", "amount": misc, "amount_lakhs": to_lakhs(misc)}
                }
            }
            content += "\n* Fees is net of GST which is taken as input tax credit."
        
        elif note_name == '21. Depreciation and Amortisation Expense':
            depreciation = calculate_note(tb_df, note_name, ['Depreciation', 'Accumulated Depreciation', 'Depreciation And Amortisation'])['total']
            amortization = calculate_note(tb_df, note_name, ['Amortization'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Depreciation & amortisation  | {total_lakhs}  | -              |
| **Total**                    | {total_lakhs}  | -              |
""".format(total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "depreciation": {"description": "Depreciation", "amount": depreciation, "amount_lakhs": to_lakhs(depreciation)},
                    "amortization": {"description": "Amortization", "amount": amortization, "amount_lakhs": to_lakhs(amortization)}
                }
            }
        
        elif note_name == '22. Loss on Sale of Assets & Investments':
            short_term_loss = calculate_note(tb_df, note_name, ['Short Term Loss on Sale of Investments'])['total']
            long_term_loss = calculate_note(tb_df, note_name, ['Long term loss on sale of investments'])['total']
            fixed_assets_loss = calculate_note(tb_df, note_name, ['Loss on Sale of Fixed Assets'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Short Term Loss on Sale of Investments (Non Derivative Loss) | {stl_lakhs} | - |
| Long term loss on sale of investments | {ltl_lakhs} | -             |
| Loss on Sale of Fixed Assets | {fal_lakhs}   | -              |
| **Total**                    | {total_lakhs} | -              |
""".format(stl_lakhs=to_lakhs(short_term_loss), ltl_lakhs=to_lakhs(long_term_loss), fal_lakhs=to_lakhs(fixed_assets_loss), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "short_term_loss": {"description": "Short Term Loss on Sale of Investments", "amount": short_term_loss, "amount_lakhs": to_lakhs(short_term_loss)},
                    "long_term_loss": {"description": "Long term loss on sale of investments", "amount": long_term_loss, "amount_lakhs": to_lakhs(long_term_loss)},
                    "fixed_assets_loss": {"description": "Loss on Sale of Fixed Assets", "amount": fixed_assets_loss, "amount_lakhs": to_lakhs(fixed_assets_loss)}
                }
            }
        
        elif note_name == '23. Finance Costs':
            bank_finance = calculate_note(tb_df, note_name, ['Bank Charges', 'Finance Charges', 'Interest', 'Interest and penalty', 'Interest on TDS'])['total']
            loan_processing = calculate_note(tb_df, note_name, ['Loan Processing'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| Bank & Finance Charges       | {bf_lakhs}     | -              |
| Loan Processing Charges      | {lp_lakhs}     | -              |
| **Total**                    | {total_lakhs}  | -              |
""".format(bf_lakhs=to_lakhs(bank_finance), lp_lakhs=to_lakhs(loan_processing), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "bank_finance": {"description": "Bank & Finance Charges", "amount": bank_finance, "amount_lakhs": to_lakhs(bank_finance)},
                    "loan_processing": {"description": "Loan Processing Charges", "amount": loan_processing, "amount_lakhs": to_lakhs(loan_processing)}
                }
            }
        
        elif note_name == '24. Payment to Auditor':
            audit_fee = calculate_note(tb_df, note_name, ['Audit Fee', 'Payment to Auditors'])['total']
            tax_audit = calculate_note(tb_df, note_name, ['Tax Audit', 'Certification Fees'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| - For Audit fee             | {audit_lakhs}  | -              |
| - For Tax Audit / Certification Fees | {tax_lakhs} | -         |
| **Total**                    | {total_lakhs}  | -              |
""".format(audit_lakhs=to_lakhs(audit_fee), tax_lakhs=to_lakhs(tax_audit), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "audit_fee": {"description": "For Audit fee", "amount": audit_fee, "amount_lakhs": to_lakhs(audit_fee)},
                    "tax_audit": {"description": "For Tax Audit / Certification Fees", "amount": tax_audit, "amount_lakhs": to_lakhs(tax_audit)}
                }
            }
        
        elif note_name == '25. Earnings in Foreign Currency':
            export_income = calculate_note(tb_df, note_name, ['Income from export of services', 'Servicing of BA/BE PROJECTS EXPORT', 'Working Standards - Export'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Inflow :**                 |                |                |
| Income from export of services | {exp_lakhs}  | -              |
| **Total**                    | {total_lakhs}  | -              |
""".format(exp_lakhs=to_lakhs(export_income), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "export_income": {"description": "Income from export of services", "amount": export_income, "amount_lakhs": to_lakhs(export_income)}
                }
            }
        
        elif note_name == '26. Particulars of Un-hedged Foreign Currency Exposure':
            export_income = calculate_note(tb_df, note_name, ['Income from export of services', 'Servicing of BA/BE PROJECTS EXPORT', 'Working Standards - Export'])['total']
            total = result['total']  # Use total from calculate_note
            content = """
"(i) There is no derivate contract outstanding as at the Balance Sheet date.
(ii) Particulars of un-hedged foreign currency exposure as at the Balance Sheet date"

| Particulars                  | March 31, 2024 | March 31, 2023 |
|------------------------------|----------------|----------------|
| **Inflow :**                 |                |                |
| Income from export of services | {exp_lakhs}  | -              |
| **Total**                    | {total_lakhs}  | -              |
""".format(exp_lakhs=to_lakhs(export_income), total_lakhs=to_lakhs(total))
            special_data = {
                "breakdown": {
                    "export_income": {"description": "Income from export of services", "amount": export_income, "amount_lakhs": to_lakhs(export_income)}
                }
            }

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
            raise FileNotFoundError(f"❌ {json_file} not found! Please ensure the trial balance JSON is available.")

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

        notes_data = generate_notes(tb_df)

        os.makedirs("output2", exist_ok=True)
        output_md = "# Notes to Financial Statements for the Year Ended March 31, 2024\n\n"
        print(f"\n📝 Generated {len(notes_data['notes'])} notes:")
        for note in notes_data['notes']:
            output_md += f"{note['markdown_content']}\n"
            if note['total_amount'] != 0:
                print(f"   ✅ {note['full_title']}: ₹{note['total_amount']:,.2f} ({note['matched_accounts_count']} accounts)")
            else:
                print(f"   ⚠  {note['full_title']}: No matching accounts found")

        with open("output2/financial_notes_16_26.md", "w", encoding="utf-8") as f:
            f.write(output_md)

        with open("output/notes_output_16_26.json", "w", encoding="utf-8") as f:
            json.dump(notes_data, f, ensure_ascii=False, indent=2)

        print(f"\n🎉 Notes 16-26 generated successfully!")
        print(f"📄 Markdown: output2/financial_notes_16_26.md")
        print(f"📊 JSON: output/notes_output_16_26.json")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'tb_df' in locals():
            print("📋 Sample trial balance data:")
            print(tb_df.head().to_string())

if __name__ == "__main__":
    main()