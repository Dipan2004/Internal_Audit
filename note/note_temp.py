import json
from datetime import datetime


note_templates = {
    "10": {
        "title": "Long Term Loans and Advances",
        "full_title": "10. Long Term Loans and Advances",
        "structure": [
            {
                "category": "In Lakhs",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Unsecured, considered good",
                "subcategories": [
                    {
                        "label": "Long Term - Security Deposits",
                        "value": "{security_deposits_2024}",
                        "previous_value": "{security_deposits_2023}"
                    }
                ],
                "total": "{unsecured_total_2024}",
                "previous_total": "{unsecured_total_2023}"
            }
        ],
        "metadata": {
            "note_number": "10",
            "generated_on": "{generated_on}"
        }
    },
    "11": {
        "title": "Inventories",
        "full_title": "11. Inventories",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Consumables",
                "subcategories": [],
                "total": "{consumables_2024}",
                "previous_total": "{consumables_2023}"
            }
        ],
        "metadata": {
            "note_number": "11",
            "generated_on": "{generated_on}"
        }
    },
    "12": {
        "title": "Trade Receivables",
        "full_title": "12. Trade Receivables",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Unsecured, considered good",
                "subcategories": [
                    {
                        "label": "Outstanding for a period exceeding six months from the date they are due for payment",
                        "value": "{over_six_months_2024}",
                        "previous_value": "{over_six_months_2023}"
                    },
                    {
                        "label": "Other receivables",
                        "value": "{other_receivables_2024}",
                        "previous_value": "{other_receivables_2023}"
                    }
                ],
                "total": "{unsecured_total_2024}",
                "previous_total": "{unsecured_total_2023}"
            },
            {
                "category": "Age wise analysis of Trade receivables as on 31.03.2024",
                "subcategories": [
                    {
                        "label": "Particulars",
                        "sub_label": "Outstanding for following periods from due date of payment",
                        "columns": [
                            {"header": "0 - 6 months", "value": "{zero_six_2024}"},
                            {"header": "6 months - 1 Year", "value": "{six_one_2024}"},
                            {"header": "1 - 2 Years", "value": "{one_two_2024}"},
                            {"header": "2 - 3 Years", "value": "{two_three_2024}"},
                            {"header": "More than 3 Years", "value": "{more_three_2024}"},
                            {"header": "Total", "value": "{age_total_2024}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_good_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_good_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_good_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_good_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{undisputed_good_more_three_2024}"},
                            {"period": "Total", "value": "{undisputed_good_total_2024}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_doubtful_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_doubtful_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_doubtful_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_doubtful_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{undisputed_doubtful_more_three_2024}"},
                            {"period": "Total", "value": "{undisputed_doubtful_total_2024}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_good_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_good_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{disputed_good_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{disputed_good_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{disputed_good_more_three_2024}"},
                            {"period": "Total", "value": "{disputed_good_total_2024}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_doubtful_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_doubtful_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{disputed_doubtful_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{disputed_doubtful_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{disputed_doubtful_more_three_2024}"},
                            {"period": "Total", "value": "{disputed_doubtful_total_2024}"}
                        ]
                    },
                    {
                        "label": "Total",
                        "values": [
                            {"period": "0 - 6 months", "value": "{total_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{total_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{total_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{total_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{total_more_three_2024}"},
                            {"period": "Total", "value": "{age_total_2024}"}
                        ]
                    }
                ]
            },
            {
                "category": "Age wise analysis of Trade receivables as on 31.03.2023",
                "subcategories": [
                    {
                        "label": "Particulars",
                        "sub_label": "Outstanding for following periods from due date of payment",
                        "columns": [
                            {"header": "0 - 6 months", "value": "{zero_six_2023}"},
                            {"header": "6 months - 1 Year", "value": "{six_one_2023}"},
                            {"header": "1 - 2 Years", "value": "{one_two_2023}"},
                            {"header": "2 - 3 Years", "value": "{two_three_2023}"},
                            {"header": "More than 3 Years", "value": "{more_three_2023}"},
                            {"header": "Total", "value": "{age_total_2023}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_good_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_good_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_good_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_good_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{undisputed_good_more_three_2023}"},
                            {"period": "Total", "value": "{undisputed_good_total_2023}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_doubtful_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_doubtful_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_doubtful_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_doubtful_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{undisputed_doubtful_more_three_2023}"},
                            {"period": "Total", "value": "{undisputed_doubtful_total_2023}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_good_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_good_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{disputed_good_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{disputed_good_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{disputed_good_more_three_2023}"},
                            {"period": "Total", "value": "{disputed_good_total_2023}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_doubtful_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_doubtful_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{disputed_doubtful_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{disputed_doubtful_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{disputed_doubtful_more_three_2023}"},
                            {"period": "Total", "value": "{disputed_doubtful_total_2023}"}
                        ]
                    },
                    {
                        "label": "Total",
                        "values": [
                            {"period": "0 - 6 months", "value": "{total_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{total_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{total_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{total_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{total_more_three_2023}"},
                            {"period": "Total", "value": "{age_total_2023}"}
                        ]
                    }
                ]
            }
        ],
        "metadata": {
            "note_number": "12",
            "generated_on": "{generated_on}"
        }
    },
    "13": {
        "title": "Cash and Bank Balances",
        "full_title": "13. Cash and Bank Balances",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Cash and cash equivalents",
                "subcategories": [
                    {
                        "label": "Balances with banks in current accounts",
                        "value": "{bank_balances_2024}",
                        "previous_value": "{bank_balances_2023}"
                    },
                    {
                        "label": "Cash on hand",
                        "value": "{cash_on_hand_2024}",
                        "previous_value": "{cash_on_hand_2023}"
                    }
                ]
            },
            {
                "category": "Other Bank Balances",
                "subcategories": [
                    {
                        "label": "Fixed Deposits with ICICI Bank",
                        "value": "{fixed_deposits_2024}",
                        "previous_value": "{fixed_deposits_2023}"
                    }
                ]
            },
            {
                "category": "Total",
                "subcategories": [],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "13",
            "generated_on": "{generated_on}"
        }
    },
    "14": {
        "title": "Short Term Loans and Advances",
        "full_title": "14. Short Term Loans and Advances",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Unsecured, considered good",
                "subcategories": [
                    {
                        "label": "Prepaid Expenses",
                        "value": "{prepaid_expenses_2024}",
                        "previous_value": "{prepaid_expenses_2023}"
                    },
                    {
                        "label": "Other Advances",
                        "value": "{other_advances_2024}",
                        "previous_value": "{other_advances_2023}"
                    }
                ]
            },
            {
                "category": "Other loans and advances",
                "subcategories": [
                    {
                        "label": "Advance tax",
                        "value": "{advance_tax_2024}",
                        "previous_value": "{advance_tax_2023}"
                    },
                    {
                        "label": "Balances with statutory/government authorities",
                        "value": "{statutory_balances_2024}",
                        "previous_value": "{statutory_balances_2023}"
                    }
                ]
            },
            {
                "category": "Total",
                "subcategories": [],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "14",
            "generated_on": "{generated_on}"
        }
    },
    "15": {
        "title": "Other Current Assets",
        "full_title": "15. Other Current Assets",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Interest accrued on fixed deposits",
                "subcategories": [],
                "total": "{interest_accrued_2024}",
                "previous_total": "{interest_accrued_2023}"
            }
        ],
        "metadata": {
            "note_number": "15",
            "generated_on": "{generated_on}"
        }
    }
}

def generate_note_template(note_number, llm_data=None):
    """Generate a note template with placeholders for LLM to fill."""
    if note_number not in note_templates:
        return None
    
    template = note_templates[note_number].copy()
    template["metadata"]["generated_on"] = datetime.now().isoformat()
    
    # Placeholder values to be replaced by LLM
    if llm_data:
        for category in template["structure"]:
            if "total" in category:
                category["total"] = llm_data.get(f"{note_number}_total_2024", "{march_2024_total}")
                category["previous_total"] = llm_data.get(f"{note_number}_total_2023", "{march_2023_total}")
            for subcat in category.get("subcategories", []):
                for key in ["value", "previous_value"]:
                    if key in subcat:
                        field_name = subcat["label"].lower().replace(" ", "_").replace("-", "_")
                        subcat[key] = llm_data.get(f"{note_number}_{field_name}_{key.split('_')[0]}", f"{{{field_name}_{key.split('_')[0]}}}")
            for subcat in category.get("columns", []):
                subcat["value"] = llm_data.get(f"{note_number}_{subcat['header'].lower().replace(' ', '_')}_2024", f"{{{subcat['header'].lower().replace(' ', '_')}_2024}}")
            for subcat in category.get("values", []):
                subcat["value"] = llm_data.get(f"{note_number}_{subcat['period'].lower().replace(' ', '_').replace('-', '_')}_{subcat['label'].lower().replace(' ', '_')}_2024", f"{{{subcat['period'].lower().replace(' ', '_').replace('-', '_')}_{subcat['label'].lower().replace(' ', '_')}_2024}}")
    
    return template

def generate_all_notes():
    """Generate templates for all notes and save to JSON."""
    all_notes = {
        "metadata": {
            "generated_on": datetime.now().isoformat(),
            "financial_year": "2024-03-31",
            "company_name": "Your Company Name",
            "total_notes": len(note_templates)
        },
        "notes": []
    }
    
    for note_number in note_templates.keys():
        note = generate_note_template(note_number)
        if note:
            all_notes["notes"].append(note)
    
    with open("note_templates.json", "w", encoding="utf-8") as f:
        json.dump(all_notes, f, indent=2, ensure_ascii=False)
    
    return all_notes

if __name__ == "__main__":
    
    notes_data = generate_all_notes()
    print("Note templates generated and saved to note_templates.json")
