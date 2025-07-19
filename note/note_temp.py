import json
from datetime import datetime



note_templates = {
    "2": {
        "title": "Share Capital",
        "full_title": "2. Share Capital",
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
                "category": "Authorised Share Capital",
                "subcategories": [
                    {
                        "label": "Equity Shares of ₹10 each",
                        "value": "{authorised_equity_2024}",
                        "previous_value": "{authorised_equity_2023}"
                    }
                ],
                "total": "{authorised_total_2024}",
                "previous_total": "{authorised_total_2023}"
            },
            {
                "category": "Issued, Subscribed and Paid-up Share Capital",
                "subcategories": [
                    {
                        "label": "Equity Shares of ₹10 each fully paid up",
                        "value": "{issued_equity_2024}",
                        "previous_value": "{issued_equity_2023}"
                    }
                ],
                "total": "{issued_total_2024}",
                "previous_total": "{issued_total_2023}"
            },
            {
                "category": "Reconciliation of Shares",
                "subcategories": [
                    {
                        "label": "Number of Shares at the beginning",
                        "value": "{shares_beginning_2024}",
                        "previous_value": "{shares_beginning_2023}"
                    },
                    {
                        "label": "Changes during the year",
                        "value": "{shares_changes_2024}",
                        "previous_value": "{shares_changes_2023}"
                    },
                    {
                        "label": "Number of Shares at the end",
                        "value": "{shares_end_2024}",
                        "previous_value": "{shares_end_2023}"
                    }
                ]
            }
        ],
        "metadata": {
            "note_number": "2",
            "generated_on": "{generated_on}"
        }
    },
    "3": {
        "title": "Reserves and Surplus",
        "full_title": "3. Reserves and Surplus",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Share Premium Account",
                        "value": "{share_premium_2024}",
                        "previous_value": "{share_premium_2023}"
                    },
                    {
                        "label": "Surplus in Statement of Profit and Loss",
                        "value": "{surplus_profit_loss_2024}",
                        "previous_value": "{surplus_profit_loss_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "3",
            "generated_on": "{generated_on}"
        }
    },
    "4": {
        "title": "Long Term Borrowings",
        "full_title": "4. Long Term Borrowings",
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
                "category": "Secured",
                "subcategories": [
                    {
                        "label": "Term Loans from Banks",
                        "value": "{term_loans_banks_2024}",
                        "previous_value": "{term_loans_banks_2023}"
                    }
                ],
                "total": "{secured_total_2024}",
                "previous_total": "{secured_total_2023}"
            }
        ],
        "metadata": {
            "note_number": "4",
            "generated_on": "{generated_on}"
        }
    },
    "5": {
        "title": "Deferred Tax Liability (Net)",
        "full_title": "5. Deferred Tax Liability (Net)",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Deferred Tax Liability",
                        "value": "{deferred_tax_liability_2024}",
                        "previous_value": "{deferred_tax_liability_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "5",
            "generated_on": "{generated_on}"
        }
    },
    "6": {
        "title": "Trade Payables",
        "full_title": "6. Trade Payables",
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
                        "label": "Outstanding for a period exceeding six months from the date they are due for payment",
                        "value": "{over_six_months_2024}",
                        "previous_value": "{over_six_months_2023}"
                    },
                    {
                        "label": "Other payables",
                        "value": "{other_payables_2024}",
                        "previous_value": "{other_payables_2023}"
                    }
                ],
                "total": "{unsecured_total_2024}",
                "previous_total": "{unsecured_total_2023}"
            },
            {
                "category": "Age wise analysis of Trade payables as on 31.03.2024",
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
                "category": "Age wise analysis of Trade payables as on 31.03.2023",
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
            "note_number": "6",
            "generated_on": "{generated_on}"
        }
    },
    "7": {
        "title": "Other Current Liabilities",
        "full_title": "7. Other Current Liabilities",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Current Maturities of Long Term Borrowings",
                        "value": "{current_maturities_2024}",
                        "previous_value": "{current_maturities_2023}"
                    },
                    {
                        "label": "Outstanding Liabilities for Expenses",
                        "value": "{outstanding_liabilities_2024}",
                        "previous_value": "{outstanding_liabilities_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "7",
            "generated_on": "{generated_on}"
        }
    },
    "8": {
        "title": "Short Term Provisions",
        "full_title": "8. Short Term Provisions",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Provision for Taxation",
                        "value": "{provision_taxation_2024}",
                        "previous_value": "{provision_taxation_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "8",
            "generated_on": "{generated_on}"
        }
    },
    "9": {
        "title": "Fixed Assets",
        "full_title": "9. Fixed Assets",
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
                "category": "Tangible Assets",
                "subcategories": [
                    {
                        "label": "Gross Block",
                        "value": "{gross_block_2024}",
                        "previous_value": "{gross_block_2023}"
                    },
                    {
                        "label": "Accumulated Depreciation",
                        "value": "{accumulated_depreciation_2024}",
                        "previous_value": "{accumulated_depreciation_2023}"
                    },
                    {
                        "label": "Net Block",
                        "value": "{net_block_2024}",
                        "previous_value": "{net_block_2023}"
                    }
                ],
                "total": "{tangible_total_2024}",
                "previous_total": "{tangible_total_2023}"
            },
            {
                "category": "Intangible Assets",
                "subcategories": [
                    {
                        "label": "Gross Block",
                        "value": "{intangible_gross_block_2024}",
                        "previous_value": "{intangible_gross_block_2023}"
                    },
                    {
                        "label": "Accumulated Amortisation",
                        "value": "{accumulated_amortisation_2024}",
                        "previous_value": "{accumulated_amortisation_2023}"
                    },
                    {
                        "label": "Net Block",
                        "value": "{intangible_net_block_2024}",
                        "previous_value": "{intangible_net_block_2023}"
                    }
                ],
                "total": "{intangible_total_2024}",
                "previous_total": "{intangible_total_2023}"
            },
            {
                "category": "Capital Work-in-Progress",
                "subcategories": [
                    {
                        "label": "Capital Work-in-Progress",
                        "value": "{cwip_2024}",
                        "previous_value": "{cwip_2023}"
                    }
                ],
                "total": "{cwip_total_2024}",
                "previous_total": "{cwip_total_2023}"
            }
        ],
        "metadata": {
            "note_number": "9",
            "generated_on": "{generated_on}"
        }
    },
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
    },
    "16": {
        "title": "Revenue from Operations",
        "full_title": "16. Revenue from Operations",
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
                "category": "Sale of Services",
                "subcategories": [
                    {
                        "label": "Domestic",
                        "value": "{domestic_2024}",
                        "previous_value": "{domestic_2023}"
                    },
                    {
                        "label": "Exports",
                        "value": "{exports_2024}",
                        "previous_value": "{exports_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "16",
            "generated_on": "{generated_on}"
        }
    },
    "17": {
        "title": "Other Income",
        "full_title": "17. Other Income",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Interest income",
                        "value": "{interestincome_2024}",
                        "previous_value": "{interestincome_2023}"
                    },
                    {
                        "label": "Foreign exchange gain (Net)",
                        "value": "{foreignexchangegainnet_2024}",
                        "previous_value": "{foreignexchangegainnet_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "17",
            "generated_on": "{generated_on}"
        }
    },
    "18": {
        "title": "Cost of Materials Consumed",
        "full_title": "18. Cost of Materials Consumed",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Opening Stock",
                        "value": "{openingstock_2024}",
                        "previous_value": "{openingstock_2023}"
                    },
                    {
                        "label": "Add: Purchases",
                        "value": "{purchases_2024}",
                        "previous_value": "{purchases_2023}"
                    },
                    {
                        "label": "",
                        "value": "{subtotal_2024}",
                        "previous_value": "{subtotal_2023}"
                    },
                    {
                        "label": "Less: Closing Stock",
                        "value": "{closingstock_2024}",
                        "previous_value": "{closingstock_2023}"
                    }
                ],
                "total": "{costmaterialsconsumed_2024}",
                "previous_total": "{costmaterialsconsumed_2023}"
            }
        ],
        "metadata": {
            "note_number": "18",
            "generated_on": "{generated_on}"
        }
    },
    "19": {
        "title": "Employee Benefit Expense",
        "full_title": "19. Employee Benefit Expense",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Salaries, wages and bonus",
                        "value": "{salarieswagesandbonus_2024}",
                        "previous_value": "{salarieswagesandbonus_2023}"
                    },
                    {
                        "label": "Contribution to PF & ESI",
                        "value": "{contributiontopfesi_2024}",
                        "previous_value": "{contributiontopfesi_2023}"
                    },
                    {
                        "label": "Staff welfare expenses",
                        "value": "{staffwelfareexpenses_2024}",
                        "previous_value": "{staffwelfareexpenses_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "19",
            "generated_on": "{generated_on}"
        }
    },
    "20": {
        "title": "Other Expenses",
        "full_title": "20. Other Expenses",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "BA / BE NOC Charges",
                        "value": "{babenoccharges_2024}",
                        "previous_value": "{babenoccharges_2023}"
                    },
                    {
                        "label": "BA Expenses",
                        "value": "{baexpenses_2024}",
                        "previous_value": "{baexpenses_2023}"
                    },
                    {
                        "label": "Payments to Volunteers",
                        "value": "{paymentstovolunteers_2024}",
                        "previous_value": "{paymentstovolunteers_2023}"
                    },
                    {
                        "label": "Other Operating Expenses",
                        "value": "{otheroperatingexpenses_2024}",
                        "previous_value": "{otheroperatingexpenses_2023}"
                    },
                    {
                        "label": "Laboratory testing charges",
                        "value": "{laboratorytestingcharges_2024}",
                        "previous_value": "{laboratorytestingcharges_2023}"
                    },
                    {
                        "label": "Rent",
                        "value": "{rent_2024}",
                        "previous_value": "{rent_2023}"
                    },
                    {
                        "label": "Rates & Taxes",
                        "value": "{ratesandtaxes_2024}",
                        "previous_value": "{ratesandtaxes_2023}"
                    },
                    {
                        "label": "Fees & licenses",
                        "value": "{feesandlicenses_2024}",
                        "previous_value": "{feesandlicenses_2023}"
                    },
                    {
                        "label": "Insurance",
                        "value": "{insurance_2024}",
                        "previous_value": "{insurance_2023}"
                    },
                    {
                        "label": "Membership & Subscription Charges",
                        "value": "{membershipandsubscriptioncharges_2024}",
                        "previous_value": "{membershipandsubscriptioncharges_2023}"
                    },
                    {
                        "label": "Postage & Communication Cost",
                        "value": "{postageandcommunicationcost_2024}",
                        "previous_value": "{postageandcommunicationcost_2023}"
                    },
                    {
                        "label": "Printing and stationery",
                        "value": "{printingandstationery_2024}",
                        "previous_value": "{printingandstationery_2023}"
                    },
                    {
                        "label": "CSR Fund Expenses",
                        "value": "{csrfundexpenses_2024}",
                        "previous_value": "{csrfundexpenses_2023}"
                    },
                    {
                        "label": "Telephone & Internet",
                        "value": "{telephoneandinternet_2024}",
                        "previous_value": "{telephoneandinternet_2023}"
                    },
                    {
                        "label": "Travelling and Conveyance",
                        "value": "{travellingandconveyance_2024}",
                        "previous_value": "{travellingandconveyance_2023}"
                    },
                    {
                        "label": "Translation Charges",
                        "value": "{translationcharges_2024}",
                        "previous_value": "{translationcharges_2023}"
                    },
                    {
                        "label": "Electricity Charges",
                        "value": "{electricitycharges_2024}",
                        "previous_value": "{electricitycharges_2023}"
                    },
                    {
                        "label": "Security Charges",
                        "value": "{securitycharges_2024}",
                        "previous_value": "{securitycharges_2023}"
                    },
                    {
                        "label": "Annual Maintenance Charges",
                        "value": "{annualmaintenancecharges_2024}",
                        "previous_value": "{annualmaintenancecharges_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Electrical",
                        "value": "{repairsandmaintenanceelectrical_2024}",
                        "previous_value": "{repairsandmaintenanceelectrical_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Office",
                        "value": "{repairsandmaintenanceoffice_2024}",
                        "previous_value": "{repairsandmaintenanceoffice_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Machinery",
                        "value": "{repairsandmaintenancemachinery_2024}",
                        "previous_value": "{repairsandmaintenancemachinery_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Vehicles",
                        "value": "{repairsandmaintenancevehicles_2024}",
                        "previous_value": "{repairsandmaintenancevehicles_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Others",
                        "value": "{repairsandmaintenanceothers_2024}",
                        "previous_value": "{repairsandmaintenanceothers_2023}"
                    },
                    {
                        "label": "Business Development Expenses",
                        "value": "{businessdevelopmentexpenses_2024}",
                        "previous_value": "{businessdevelopmentexpenses_2023}"
                    },
                    {
                        "label": "Professional & Consultancy Fees",
                        "value": "{professionalandconsultancyfees_2024}",
                        "previous_value": "{professionalandconsultancyfees_2023}"
                    },
                    {
                        "label": "Payment to Auditors",
                        "value": "{paymenttoauditors_2024}",
                        "previous_value": "{paymenttoauditors_2023}"
                    },
                    {
                        "label": "Bad Debts Written Off",
                        "value": "{baddebtswrittenoff_2024}",
                        "previous_value": "{baddebtswrittenoff_2023}"
                    },
                    {
                        "label": "Fire Extinguishers Refilling Charges",
                        "value": "{fireextinguishersrefillingcharges_2024}",
                        "previous_value": "{fireextinguishersrefillingcharges_2023}"
                    },
                    {
                        "label": "Food Expenses for Guests",
                        "value": "{foodexpensesforguests_2024}",
                        "previous_value": "{foodexpensesforguests_2023}"
                    },
                    {
                        "label": "Diesel Expenses",
                        "value": "{dieselexpenses_2024}",
                        "previous_value": "{dieselexpenses_2023}"
                    },
                    {
                        "label": "Interest Under 234 C Fy 2021-22",
                        "value": "{interestunder234cfy202122_2024}",
                        "previous_value": "{interestunder234cfy202122_2023}"
                    },
                    {
                        "label": "Loan Processing Charges",
                        "value": "{loanprocessingcharges_2024}",
                        "previous_value": "{loanprocessingcharges_2023}"
                    },
                    {
                        "label": "Sitting Fee of Directors",
                        "value": "{sittingfeeofdirectors_2024}",
                        "previous_value": "{sittingfeeofdirectors_2023}"
                    },
                    {
                        "label": "Customs Duty Payment",
                        "value": "{customsdutypayment_2024}",
                        "previous_value": "{customsdutypayment_2023}"
                    },
                    {
                        "label": "Transportation and Unloading Charges",
                        "value": "{transportationandunloadingcharges_2024}",
                        "previous_value": "{transportationandunloadingcharges_2023}"
                    },
                    {
                        "label": "Software Equipment",
                        "value": "{softwareequipment_2024}",
                        "previous_value": "{softwareequipment_2023}"
                    },
                    {
                        "label": "Miscellaneous expenses",
                        "value": "{miscellaneousexpenses_2024}",
                        "previous_value": "{miscellaneousexpenses_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "20",
            "generated_on": "{generated_on}"
        },
        "notes_and_disclosures": [
            "* Fees is net of GST which is taken as input tax credit."
        ]
    },
    "21": {
        "title": "Depreciation and Amortisation Expense",
        "full_title": "21. Depreciation and Amortisation Expense",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Depreciation & amortisation",
                        "value": "{depreciationamortisation_2024}",
                        "previous_value": "{depreciationamortisation_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "21",
            "generated_on": "{generated_on}"
        }
    },
    "22": {
        "title": "Loss on Sale of Assets & Investments",
        "full_title": "22. Loss on Sale of Assets & Investments",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Short Term Loss on Sale of Investments (Non Derivative Loss)",
                        "value": "{shorttermlossonSaleofinvestmentsnonderivativeLoss_2024}",
                        "previous_value": "{shorttermlossonSaleofinvestmentsnonderivativeLoss_2023}"
                    },
                    {
                        "label": "Long term loss on sale of investments",
                        "value": "{longtermlossonSaleofinvestments_2024}",
                        "previous_value": "{longtermlossonSaleofinvestments_2023}"
                    },
                    {
                        "label": "Loss on Sale of Fixed Assets",
                        "value": "{lossonSaleoffixedassets_2024}",
                        "previous_value": "{lossonSaleoffixedassets_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "22",
            "generated_on": "{generated_on}"
        }
    },
    "23": {
        "title": "Finance Costs",
        "full_title": "23. Finance Costs",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Bank & Finance Charges",
                        "value": "{bankfinancecharges_2024}",
                        "previous_value": "{bankfinancecharges_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "23",
            "generated_on": "{generated_on}"
        }
    },
    "24": {
        "title": "Payment to Auditor",
        "full_title": "24. Payment to Auditor",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "For Audit fee",
                        "value": "{forauditfee_2024}",
                        "previous_value": "{forauditfee_2023}"
                    },
                    {
                        "label": "For Tax Audit / Certification Fees",
                        "value": "{fortaxauditcertificationfees_2024}",
                        "previous_value": "{fortaxauditcertificationfees_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "24",
            "generated_on": "{generated_on}"
        }
    },
    "25": {
        "title": "Earnings in Foreign Currency",
        "full_title": "25. Earnings in Foreign Currency",
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
                "category": "Inflow",
                "subcategories": [
                    {
                        "label": "Income from export of services",
                        "value": "{incomefromexportofservices_2024}",
                        "previous_value": "{incomefromexportofservices_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "25",
            "generated_on": "{generated_on}"
        }
    },
    "26": {
        "title": "Particulars of Un-hedged Foreign Currency Exposure",
        "full_title": "26. Particulars of Un-hedged Foreign Currency Exposure",
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
                "category": "Inflow",
                "subcategories": [
                    {
                        "label": "Income from export of services",
                        "value": "{incomefromexportofservices_2024}",
                        "previous_value": "{incomefromexportofservices_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "26",
            "generated_on": "{generated_on}"
        },
        "notes_and_disclosures": [
            "(i) There is no derivate contract outstanding as at the Balance Sheet date.",
            "(ii) Particulars of un-hedged foreign currency exposure as at the Balance Sheet date"
        ]
    },
    "27": {
        "title": "Contingent Liabilities",
        "full_title": "27. Contingent Liabilities",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Claims against the company not acknowledged as debts",
                        "value": "{claims_not_acknowledged_2024}",
                        "previous_value": "{claims_not_acknowledged_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "27",
            "generated_on": "{generated_on}"
        }
    },
    "28": {
        "title": "Commitments",
        "full_title": "28. Commitments",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Capital Commitments",
                        "value": "{capital_commitments_2024}",
                        "previous_value": "{capital_commitments_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "28",
            "generated_on": "{generated_on}"
        }
    },
    "29": {
        "title": "Related Party Disclosures",
        "full_title": "29. Related Party Disclosures",
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
                "category": "Key Management Personnel",
                "subcategories": [
                    {
                        "label": "Remuneration",
                        "value": "{remuneration_kmp_2024}",
                        "previous_value": "{remuneration_kmp_2023}"
                    }
                ],
                "total": "{total_kmp_2024}",
                "previous_total": "{total_kmp_2023}"
            }
        ],
        "metadata": {
            "note_number": "29",
            "generated_on": "{generated_on}"
        }
    },
    "30": {
        "title": "Segment Reporting",
        "full_title": "30. Segment Reporting",
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
                "category": "Segment Revenue",
                "subcategories": [
                    {
                        "label": "Segment A",
                        "value": "{segment_a_revenue_2024}",
                        "previous_value": "{segment_a_revenue_2023}"
                    },
                    {
                        "label": "Segment B",
                        "value": "{segment_b_revenue_2024}",
                        "previous_value": "{segment_b_revenue_2023}"
                    }
                ],
                "total": "{segment_total_2024}",
                "previous_total": "{segment_total_2023}"
            }
        ],
        "metadata": {
            "note_number": "30",
            "generated_on": "{generated_on}"
        }
    },
    "31": {
        "title": "Earnings Per Share (EPS)",
        "full_title": "31. Earnings Per Share (EPS)",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Basic EPS",
                        "value": "{basic_eps_2024}",
                        "previous_value": "{basic_eps_2023}"
                    },
                    {
                        "label": "Diluted EPS",
                        "value": "{diluted_eps_2024}",
                        "previous_value": "{diluted_eps_2023}"
                    }
                ],
                "total": "{total_eps_2024}",
                "previous_total": "{total_eps_2023}"
            }
        ],
        "metadata": {
            "note_number": "31",
            "generated_on": "{generated_on}"
        }
    },
    "32": {
        "title": "Additional Disclosures",
        "full_title": "32. Additional Disclosures",
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
                "category": "",
                "subcategories": [
                    {
                        "label": "Additional Information A",
                        "value": "{additional_info_a_2024}",
                        "previous_value": "{additional_info_a_2023}"
                    },
                    {
                        "label": "Additional Information B",
                        "value": "{additional_info_b_2024}",
                        "previous_value": "{additional_info_b_2023}"
                    }
                ],
                "total": "{total_additional_2024}",
                "previous_total": "{total_additional_2023}"
            }
        ],
        "metadata": {
            "note_number": "32",
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
                        field_name = subcat["label"].lower().replace(" ", "").replace("-", "")
                        subcat[key] = llm_data.get(f"{note_number}{field_name}{key.split('_')[0]}", f"{{{field_name}{key.split('_')[0]}}}")
            for subcat in category.get("columns", []):
                subcat["value"] = llm_data.get(f"{note_number}{subcat['header'].lower().replace(' ', '')}2024", f"{{{subcat['header'].lower().replace(' ', '')}_2024}}")
            for subcat in category.get("values", []):
                subcat["value"] = llm_data.get(f"{note_number}{subcat['period'].lower().replace(' ', '').replace('-', '')}{subcat['label'].lower().replace(' ', '')}_2024", f"{{{subcat['period'].lower().replace(' ', '').replace('-', '')}{subcat['label'].lower().replace(' ', '_')}_2024}}")
    
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