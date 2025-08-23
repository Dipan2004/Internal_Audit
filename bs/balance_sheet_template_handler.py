import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BalanceSheetItem(BaseModel):
    section: str
    category: str
    subcategory: Optional[str] = ""
    name: str
    note: str
    indent_level: int = 1
    is_total_row: bool = False
    is_section_header: bool = False
    is_category_header: bool = False

class FormattingRules(BaseModel):
    header: Dict[str, Any]
    sections: Dict[str, Dict[str, Any]]
    categories: Dict[str, Dict[str, Any]]
    subcategories: Dict[str, Dict[str, Any]]
    totals: Dict[str, Dict[str, Any]]

class BalanceSheetTemplate:
    """
    Provides the structure, formatting, and field mappings for a standard Balance Sheet.
    """

    def __init__(self):
        # Updated Complete Balance Sheet Structure Template
        self.template_structure: List[Dict[str, Any]] = [
            # EQUITY AND LIABILITIES
            # (1) Shareholders' funds
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Shareholders' funds", subcategory="", name="Share capital", note="2").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Shareholders' funds", subcategory="", name="Reserves and surplus", note="3").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Shareholders' funds", subcategory="", name="Money received against share warrants", note=" ").dict(),
            
            # (2) Share application money pending allotment
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Share application money pending allotment", subcategory="", name="Share application money pending allotment", note=" ").dict(),
            
            # (3) Non-current liabilities
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Non-Current liabilities", subcategory="", name="Long-term borrowings", note="4").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Non-Current liabilities", subcategory="", name="Deferred tax liabilities (Net)", note="5").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Non-Current liabilities", subcategory="", name="Other Long-term liabilities", note="8").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Non-Current liabilities", subcategory="", name="Long-term provisions", note="9").dict(),
            
            # (4) Current liabilities
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Current liabilities", subcategory="", name="Short-term borrowings", note="10").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Current liabilities", subcategory="Trade payables", name="total outstanding dues of micro enterprises and small enterprises", note=" ", indent_level=2).dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Current liabilities", subcategory="Trade payables", name="total outstanding dues of creditors other than micro enterprises and small enterprises", note=" ", indent_level=2).dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Current liabilities", subcategory="", name="Other current liabilities", note="7").dict(),
            BalanceSheetItem(section="EQUITY AND LIABILITIES", category="Current liabilities", subcategory="", name="Short-term provisions", note="8").dict(),
            
            # ASSETS
            # Non-current assets
            # (1) Property, Plant and Equipment
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="Property, Plant and Equipment", name="Tangible assets", note="9", indent_level=2).dict(),
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="Property, Plant and Equipment", name="Intangible assets", note="9", indent_level=2).dict(),
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="Property, Plant and Equipment", name="Capital work-in-progress", note=" ", indent_level=2).dict(),
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="Property, Plant and Equipment", name="Intangible assets under development", note="9", indent_level=2).dict(),
            
            # Other Non-current assets
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="", name="Non-current investments", note=" ").dict(),
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="", name="Deferred tax assets (net)", note=" ").dict(),
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="", name="Long-term loans and advances", note="10").dict(),
            BalanceSheetItem(section="ASSETS", category="Non-current assets", subcategory="", name="Other non-current assets", note=" ").dict(),
            
            # (2) Current assets
            BalanceSheetItem(section="ASSETS", category="Current assets", subcategory="", name="Current investments", note=" ").dict(),
            BalanceSheetItem(section="ASSETS", category="Current assets", subcategory="", name="Inventories", note="11").dict(),
            BalanceSheetItem(section="ASSETS", category="Current assets", subcategory="", name="Trade receivables", note="12").dict(),
            BalanceSheetItem(section="ASSETS", category="Current assets", subcategory="", name="Cash and cash equivalents", note="13").dict(),
            BalanceSheetItem(section="ASSETS", category="Current assets", subcategory="", name="Short-term loans and advances", note="14").dict(),
            BalanceSheetItem(section="ASSETS", category="Current assets", subcategory="", name="Other current assets", note="15").dict()
        ]

        # Formatting rules for display
        self.formatting_rules: FormattingRules = FormattingRules(
            header={
                "title": "Balance Sheet as at March 31, 2024",
                "currency_note": "(Rupees in...........)",
                "column_headers": ["Particulars", "Note No.", "Figures as at the end of current reporting period", "Figures as at the end of the previous reporting period"]
            },
            sections={
                "EQUITY AND LIABILITIES": {"display_name": "EQUITY AND LIABILITIES", "order": 1},
                "ASSETS": {"display_name": "ASSETS", "order": 2}
            },
            categories={
                "Shareholders' funds": {"display_name": "Shareholders' funds", "show_total": True, "total_label": "", "order": 1},
                "Share application money pending allotment": {"display_name": "Share application money pending allotment", "show_total": True, "total_label": "", "order": 2},
                "Non-Current liabilities": {"display_name": "Non-Current liabilities", "show_total": True, "total_label": "", "order": 3},
                "Current liabilities": {"display_name": "Current liabilities", "show_total": True, "total_label": "", "order": 4},
                "Non-current assets": {"display_name": "Non-current assets", "show_total": True, "total_label": "", "order": 5},
                "Current assets": {"display_name": "Current assets", "show_total": True, "total_label": "", "order": 6}
            },
            subcategories={
                "Property, Plant and Equipment": {"display_name": "Property, Plant and Equipment", "show_total": True, "total_label": "", "parent_category": "Non-current assets"},
                "Trade payables": {"display_name": "Trade payables", "show_total": True, "total_label": "", "parent_category": "Current liabilities"}
            },
            totals={
                "TOTAL_EQUITY_LIABILITIES": {"display_name": "TOTAL", "position": "after_equity_liabilities", "is_grand_total": True},
                "TOTAL_ASSETS": {"display_name": "TOTAL", "position": "after_assets", "is_grand_total": True}
            }
        )

        # Updated Field mapping patterns for data extraction
        self.field_mappings: Dict[str, List[str]] = {
            'share_capital': ['share capital', 'equity share', 'paid up', 'issued shares', 'authorised shares', 'subscribed', 'fully paid'],
            'reserves_surplus': ['reserves and surplus', 'reserves', 'surplus', 'retained earnings', 'profit and loss', 'general reserves', 'closing balance'],
            'money_against_warrants': ['money received against share warrants', 'share warrants', 'warrants'],
            'share_application_money': ['share application money', 'application money pending', 'pending allotment'],
            'long_term_borrowings': ['long term borrowings', 'long-term borrowings', 'borrowings', 'debt', 'loans', 'financial corporation', 'bank loan'],
            'deferred_tax_liabilities': ['deferred tax liabilities', 'deferred tax liability', 'tax liability'],
            'other_long_term_liabilities': ['other long-term liabilities', 'long term liabilities', 'other long term'],
            'long_term_provisions': ['long-term provisions', 'long term provisions', 'provisions'],
            'short_term_borrowings': ['short-term borrowings', 'short term borrowings', 'current borrowings'],
            'trade_payables_micro': ['total outstanding dues of micro enterprises', 'micro enterprises', 'small enterprises dues'],
            'trade_payables_others': ['total outstanding dues of creditors other than micro', 'other creditors', 'creditors other than micro'],
            'other_current_liabilities': ['other current liabilities', 'current maturities', 'outstanding liabilities', 'statutory dues', 'accrued expenses'],
            'short_term_provisions': ['short term provisions', 'provisions', 'provision for taxation', 'tax provision'],
            'tangible_assets': ['tangible assets', 'property plant', 'fixed assets', 'buildings', 'plant', 'equipment', 'net carrying value'],
            'intangible_assets': ['intangible assets', 'software', 'goodwill', 'intangible'],
            'capital_work_progress': ['capital work-in-progress', 'work in progress', 'construction in progress', 'CWIP'],
            'intangible_under_development': ['intangible assets under development', 'intangible under development', 'development'],
            'non_current_investments': ['non-current investments', 'long term investments', 'investments'],
            'deferred_tax_assets': ['deferred tax assets', 'tax assets'],
            'long_term_loans_advances': ['long term loans', 'security deposits', 'long term advances'],
            'other_non_current_assets': ['other non-current assets', 'other long term assets'],
            'current_investments': ['current investments', 'short term investments', 'marketable securities'],
            'inventories': ['inventories', 'stock', 'consumables', 'raw materials'],
            'trade_receivables': ['trade receivables', 'receivables', 'debtors', 'outstanding', 'other receivables'],
            'cash_equivalents': ['cash and cash equivalents', 'cash', 'bank balances', 'current accounts', 'cash on hand', 'fixed deposits'],
            'short_term_loans_advances': ['short term loans', 'prepaid expenses', 'other advances', 'advance tax', 'statutory authorities'],
            'other_current_assets': ['other current assets', 'accrued income', 'interest accrued']
        }

    def get_template_structure(self) -> List[Dict[str, Any]]:
        """Return the complete template structure."""
        return self.template_structure.copy()

    def get_formatting_rules(self) -> FormattingRules:
        """Return the formatting rules."""
        return self.formatting_rules.copy()

    def get_field_mappings(self) -> Dict[str, List[str]]:
        """Return the field mapping patterns."""
        return self.field_mappings.copy()

    def get_categories(self) -> List[str]:
        """Get unique categories from template."""
        categories = []
        seen = set()
        for item in self.template_structure:
            cat = item["category"]
            if cat not in seen:
                categories.append(cat)
                seen.add(cat)
        return categories

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all items for a specific category."""
        return [item for item in self.template_structure if item["category"] == category]

    def get_items_by_section(self, section: str) -> List[Dict[str, Any]]:
        """Get all items for a specific section."""
        return [item for item in self.template_structure if item["section"] == section]

    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a specific category."""
        subcats = set()
        for item in self.template_structure:
            if item["category"] == category and item["subcategory"]:
                subcats.add(item["subcategory"])
        return list(subcats)

# For backward compatibility - alias the class
BalanceSheet = BalanceSheetTemplate

# Updated Module level constants for quick access
BALANCE_SHEET_SECTIONS: List[str] = ["EQUITY AND LIABILITIES", "ASSETS"]

BALANCE_SHEET_CATEGORIES: List[str] = [
    "Shareholders' funds",
    "Share application money pending allotment",
    "Non-Current liabilities",
    "Current liabilities",
    "Non-current assets",
    "Current assets"
]

STANDARD_NOTES_MAPPING: Dict[str, str] = {
    "Share capital": "2",
    "Reserves and surplus": "3", 
    "Money received against share warrants": " ",
    "Share application money pending allotment": " ",
    "Long-term borrowings": "4",
    "Deferred tax liabilities (Net)": "5", 
    "Other Long-term liabilities": "8",
    "Long-term provisions": "9",
    "Short-term borrowings": " ",
    "total outstanding dues of micro enterprises and small enterprises": " ",
    "total outstanding dues of creditors other than micro enterprises and small enterprises": " ", 
    "Other current liabilities": "7",
    "Short-term provisions": "8",
    "Tangible assets": "9",
    "Intangible assets": "9",
    "Capital work-in-progress": " ", 
    "Intangible assets under development": "9",
    "Non-current investments": " ",
    "Deferred tax assets (net)": " ",
    "Long-term loans and advances": "10",
    "Other non-current assets": " ",
    "Current investments": " ",
    "Inventories": "11",
    "Trade receivables": "12", 
    "Cash and cash equivalents": "13",
    "Short-term loans and advances": "14",
    "Other current assets": "15"
}

SIMPLE_TEMPLATE: List[Dict[str, Any]] = [
    {"category": "Shareholders' funds", "name": "Share capital", "note": "2"},
    {"category": "Shareholders' funds", "name": "Reserves and surplus", "note": "3"},
    {"category": "Shareholders' funds", "name": "Money received against share warrants", "note": " "},
    {"category": "Share application money pending allotment", "name": "Share application money pending allotment", "note": " "},
    {"category": "Non-Current liabilities", "name": "Long-term borrowings", "note": "4"},
    {"category": "Non-Current liabilities", "name": "Deferred tax liabilities (Net)", "note": "5"},
    {"category": "Non-Current liabilities", "name": "Other Long-term liabilities", "note": "8"},
    {"category": "Non-Current liabilities", "name": "Long-term provisions", "note": "9"},
    {"category": "Current liabilities", "name": "Short-term borrowings", "note": " "},
    {"category": "Current liabilities", "subcategory": "Trade payables", "name": "total outstanding dues of micro enterprises and small enterprises", "note": " "},
    {"category": "Current liabilities", "subcategory": "Trade payables", "name": "total outstanding dues of creditors other than micro enterprises and small enterprises", "note": " "},
    {"category": "Current liabilities", "name": "Other current liabilities", "note": "7"},
    {"category": "Current liabilities", "name": "Short-term provisions", "note": "8"},
    {"category": "Non-current assets", "subcategory": "Property, Plant and Equipment", "name": "Tangible assets", "note": "9"},
    {"category": "Non-current assets", "subcategory": "Property, Plant and Equipment", "name": "Intangible assets", "note": "9"},
    {"category": "Non-current assets", "subcategory": "Property, Plant and Equipment", "name": "Capital work-in-progress", "note": " "},
    {"category": "Non-current assets", "subcategory": "Property, Plant and Equipment", "name": "Intangible assets under development", "note": "9"},
    {"category": "Non-current assets", "name": "Non-current investments", "note": " "},
    {"category": "Non-current assets", "name": "Deferred tax assets (net)", "note": " "},
    {"category": "Non-current assets", "name": "Long-term loans and advances", "note": "10"},
    {"category": "Non-current assets", "name": "Other non-current assets", "note": " "},
    {"category": "Current assets", "name": "Current investments", "note": " "},
    {"category": "Current assets", "name": "Inventories", "note": "11"},
    {"category": "Current assets", "name": "Trade receivables", "note": "12"},
    {"category": "Current assets", "name": "Cash and cash equivalents", "note": "13"},
    {"category": "Current assets", "name": "Short-term loans and advances", "note": "14"},
    {"category": "Current assets", "name": "Other current assets", "note": "15"}
]