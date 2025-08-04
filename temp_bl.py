class BalanceSheetTemplate:
    
    def __init__(self):
        # Complete Balance Sheet Structure Template
        self.template_structure = [
           
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Shareholders' funds",
                "subcategory": "",
                "name": "Share capital",
                "note": "2",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Shareholders' funds", 
                "subcategory": "",
                "name": "Reserves and surplus",
                "note": "3",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            
            # Non-Current liabilities
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Non-Current liabilities",
                "subcategory": "",
                "name": "Long term borrowings",
                "note": "4",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Non-Current liabilities",
                "subcategory": "",
                "name": "Deferred Tax Liability (Net)",
                "note": "5",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            
            # Current liabilities
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Current liabilities",
                "subcategory": "",
                "name": "Trade payables",
                "note": "6",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Current liabilities",
                "subcategory": "",
                "name": "Other current liabilities", 
                "note": "7",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "EQUITY AND LIABILITIES",
                "category": "Current liabilities",
                "subcategory": "",
                "name": "Short term provisions",
                "note": "8",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            
            # ASSETS
            # ======
            
            # Non-current assets - Fixed assets
            {
                "section": "ASSETS",
                "category": "Non-current assets",
                "subcategory": "Fixed assets",
                "name": "Tangible assets",
                "note": "9",
                "indent_level": 2,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "ASSETS",
                "category": "Non-current assets",
                "subcategory": "Fixed assets", 
                "name": "Intangible assets",
                "note": "9",
                "indent_level": 2,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            
            # Non-current assets - Other
            {
                "section": "ASSETS",
                "category": "Non-current assets",
                "subcategory": "",
                "name": "Long Term Loans and Advances",
                "note": "10",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            
            # Current assets
            {
                "section": "ASSETS",
                "category": "Current assets",
                "subcategory": "",
                "name": "Inventories",
                "note": "11",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "ASSETS",
                "category": "Current assets",
                "subcategory": "",
                "name": "Trade receivables",
                "note": "12",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "ASSETS",
                "category": "Current assets",
                "subcategory": "",
                "name": "Cash and bank balances",
                "note": "13",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "ASSETS",
                "category": "Current assets",
                "subcategory": "",
                "name": "Short-term loans and advances",
                "note": "14",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            },
            {
                "section": "ASSETS", 
                "category": "Current assets",
                "subcategory": "",
                "name": "Other current assets",
                "note": "15",
                "indent_level": 1,
                "is_total_row": False,
                "is_section_header": False,
                "is_category_header": False
            }
        ]
        
        # Define the display structure and formatting rules
        self.formatting_rules = {
            "header": {
                "title": "Balance Sheet as at March 31, 2024",
                "currency_note": "(In Lakhs)",
                "column_headers": ["", "Notes", "March 31, 2024", "March 31, 2023"]
            },
            "sections": {
                "EQUITY AND LIABILITIES": {
                    "display_name": "EQUITY AND LIABILITIES",
                    "order": 1
                },
                "ASSETS": {
                    "display_name": "ASSETS", 
                    "order": 2
                }
            },
            "categories": {
                "Shareholders' funds": {
                    "display_name": "Shareholders' funds",
                    "show_total": True,
                    "total_label": "",
                    "order": 1
                },
                "Non-Current liabilities": {
                    "display_name": "Non-Current liabilities",
                    "show_total": True,
                    "total_label": "",
                    "order": 2
                },
                "Current liabilities": {
                    "display_name": "Current liabilities", 
                    "show_total": True,
                    "total_label": "",
                    "order": 3
                },
                "Non-current assets": {
                    "display_name": "Non-current assets",
                    "show_total": True, 
                    "total_label": "",
                    "order": 4
                },
                "Current assets": {
                    "display_name": "Current assets",
                    "show_total": True,
                    "total_label": "",
                    "order": 5
                }
            },
            "subcategories": {
                "Fixed assets": {
                    "display_name": "Fixed assets",
                    "show_total": True,
                    "total_label": "",
                    "parent_category": "Non-current assets"
                }
            },
            "totals": {
                "TOTAL_EQUITY_LIABILITIES": {
                    "display_name": "TOTAL",
                    "position": "after_equity_liabilities",
                    "is_grand_total": True
                },
                "TOTAL_ASSETS": {
                    "display_name": "TOTAL", 
                    "position": "after_assets",
                    "is_grand_total": True
                }
            }
        }
        
        # Field mapping patterns for data extraction
        self.field_mappings = {
            'share_capital': [
                'share capital', 'equity share', 'paid up', 'issued shares', 
                'authorised shares', 'subscribed', 'fully paid'
            ],
            'reserves_surplus': [
                'reserves and surplus', 'reserves', 'surplus', 'retained earnings',
                'profit and loss', 'general reserves', 'closing balance'
            ],
            'long_term_borrowings': [
                'long term borrowings', 'long-term borrowings', 'borrowings',
                'debt', 'loans', 'financial corporation', 'bank loan'
            ],
            'deferred_tax': [
                'deferred tax', 'tax liability', 'deferred tax liability'
            ],
            'trade_payables': [
                'trade payables', 'payables', 'creditors', 'sundry creditors',
                'capital expenditure', 'other expenses'
            ],
            'other_current_liabilities': [
                'other current liabilities', 'current maturities', 'outstanding liabilities',
                'statutory dues', 'accrued expenses'
            ],
            'short_term_provisions': [
                'short term provisions', 'provisions', 'provision for taxation',
                'tax provision'
            ],
            'tangible_assets': [
                'tangible assets', 'property plant', 'fixed assets', 'buildings',
                'plant', 'equipment', 'net carrying value'
            ],
            'intangible_assets': [
                'intangible assets', 'software', 'goodwill', 'intangible'
            ],
            'long_term_loans_advances': [
                'long term loans', 'security deposits', 'long term advances'
            ],
            'inventories': [
                'inventories', 'stock', 'consumables', 'raw materials'
            ],
            'trade_receivables': [
                'trade receivables', 'receivables', 'debtors', 'outstanding',
                'other receivables'
            ],
            'cash_bank': [
                'cash and bank', 'cash', 'bank balances', 'current accounts',
                'cash on hand', 'fixed deposits'
            ],
            'short_term_loans_advances': [
                'short term loans', 'prepaid expenses', 'other advances',
                'advance tax', 'statutory authorities'
            ],
            'other_current_assets': [
                'other current assets', 'accrued income', 'interest accrued'
            ]
        }
    
    def get_template_structure(self):
        """Return the complete template structure"""
        return self.template_structure.copy()
    
    def get_formatting_rules(self):
        """Return the formatting rules"""
        return self.formatting_rules.copy()
    
    def get_field_mappings(self):
        """Return the field mapping patterns"""
        return self.field_mappings.copy()
    
    def get_categories(self):
        """Get unique categories from template"""
        categories = []
        seen = set()
        for item in self.template_structure:
            cat = item["category"]
            if cat not in seen:
                categories.append(cat)
                seen.add(cat)
        return categories
    
    def get_items_by_category(self, category):
        """Get all items for a specific category"""
        return [item for item in self.template_structure if item["category"] == category]
    
    def get_items_by_section(self, section):
        """Get all items for a specific section"""
        return [item for item in self.template_structure if item["section"] == section]
    
    def get_subcategories(self, category):
        """Get subcategories for a specific category"""
        subcats = set()
        for item in self.template_structure:
            if item["category"] == category and item["subcategory"]:
                subcats.add(item["subcategory"])
        return list(subcats)


# For backward compatibility - alias the class
BalanceSheet = BalanceSheetTemplate

# Alternative access - Module level constants
BALANCE_SHEET_SECTIONS = ["EQUITY AND LIABILITIES", "ASSETS"]

BALANCE_SHEET_CATEGORIES = [
    "Shareholders' funds",
    "Non-Current liabilities",
    "Current liabilities",
    "Non-current assets",
    "Current assets"
]

STANDARD_NOTES_MAPPING = {
    "Share capital": "2",
    "Reserves and surplus": "3",
    "Long term borrowings": "4", 
    "Deferred Tax Liability (Net)": "5",
    "Trade payables": "6",
    "Other current liabilities": "7",
    "Short term provisions": "8",
    "Tangible assets": "9",
    "Intangible assets": "9", 
    "Long Term Loans and Advances": "10",
    "Inventories": "11",
    "Trade receivables": "12",
    "Cash and bank balances": "13",
    "Short-term loans and advances": "14",
    "Other current assets": "15"
}

# Quick access template for simple use cases
SIMPLE_TEMPLATE = [
    {"category": "Shareholders' funds", "name": "Share capital", "note": "2"},
    {"category": "Shareholders' funds", "name": "Reserves and surplus", "note": "3"},
    {"category": "Non-Current liabilities", "name": "Long term borrowings", "note": "4"},
    {"category": "Non-Current liabilities", "name": "Deferred Tax Liability (Net)", "note": "5"},
    {"category": "Current liabilities", "name": "Trade payables", "note": "6"},
    {"category": "Current liabilities", "name": "Other current liabilities", "note": "7"},
    {"category": "Current liabilities", "name": "Short term provisions", "note": "8"},
    {"category": "Non-current assets", "subcategory": "Fixed assets", "name": "Tangible assets", "note": "9"},
    {"category": "Non-current assets", "subcategory": "Fixed assets", "name": "Intangible assets", "note": "9"},
    {"category": "Non-current assets", "name": "Long Term Loans and Advances", "note": "10"},
    {"category": "Current assets", "name": "Inventories", "note": "11"},
    {"category": "Current assets", "name": "Trade receivables", "note": "12"},
    {"category": "Current assets", "name": "Cash and bank balances", "note": "13"},
    {"category": "Current assets", "name": "Short-term loans and advances", "note": "14"},
    {"category": "Current assets", "name": "Other current assets", "note": "15"}
]