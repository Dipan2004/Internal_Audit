import os
import json
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill
import requests
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BalanceSheetGenerator:
    def __init__(self, openrouter_api_key: str):
        """Initialize the balance sheet generator with OpenRouter API key."""
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Standard balance sheet structure mapping
        self.balance_sheet_structure = {
            "equity_and_liabilities": {
                "shareholders_funds": [
                    "share capital", "equity share capital", "share capital", "paid up capital",
                    "reserves and surplus", "retained earnings", "general reserves", "capital reserves"
                ],
                "non_current_liabilities": [
                    "long term borrowings", "long term loans", "deferred tax liability", "provisions",
                    "long term provisions", "employee benefit obligations"
                ],
                "current_liabilities": [
                    "trade payables", "current liabilities", "short term borrowings", 
                    "other current liabilities", "short term provisions", "current portion"
                ]
            },
            "assets": {
                "non_current_assets": [
                    "fixed assets", "property plant equipment", "tangible assets", "intangible assets",
                    "capital work in progress", "long term loans and advances", "investments",
                    "goodwill", "land", "building", "plant and machinery"
                ],
                "current_assets": [
                    "inventories", "trade receivables", "cash and bank balances", "cash and cash equivalents",
                    "short term loans and advances", "other current assets", "marketable securities",
                    "prepaid expenses", "advance tax"
                ]
            }
        }

    def safe_float_conversion(self, value: Any) -> float:
        """Safely convert value to float, handling various formats."""
        if value is None:
            return 0.0
        
        str_val = str(value).strip()
        
        if not str_val or str_val in ['-', '--', '', 'None', 'null', 'NaN']:
            return 0.0
        
        # Remove formatting
        str_val = str_val.replace(',', '').replace('₹', '').replace('Rs.', '').replace(' ', '')
        str_val = str_val.replace('(', '-').replace(')', '')  # Handle negative values in parentheses
        
        try:
            return float(str_val)
        except (ValueError, TypeError):
            return 0.0

    def call_openrouter_api(self, messages: List[Dict], model: str = "mistralai/mixtral-8x7b-instruct") -> str:
        """Call OpenRouter API with fallback model support."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://balance-sheet-generator.com",
            "X-Title": "Balance Sheet Generator",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ Error with {model}: {str(e)}")
            
            # Fallback to Claude or GPT-4
            fallback_models = [
                "anthropic/claude-3-sonnet",
                "openai/gpt-4-turbo",
                "meta-llama/llama-3.1-70b-instruct"
            ]
            
            for fallback_model in fallback_models:
                try:
                    print(f"🔄 Trying fallback model: {fallback_model}")
                    payload["model"] = fallback_model
                    response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
                    response.raise_for_status()
                    result = response.json()
                    return result['choices'][0]['message']['content']
                except Exception as fallback_error:
                    print(f"❌ Fallback {fallback_model} failed: {str(fallback_error)}")
                    continue
            
            raise Exception("All API models failed")

    def extract_financial_data_with_ai(self, json_data: Dict) -> Dict:
        """Use AI to extract and categorize financial data from JSON."""
        
        # Convert JSON to string for AI analysis
        json_str = json.dumps(json_data, indent=2)[:8000]  # Limit size for API
        
        prompt_messages = [
            {
                "role": "system",
                "content": """You are an expert financial data analyst. Your task is to extract balance sheet items from the provided JSON data and categorize them correctly.

CRITICAL INSTRUCTIONS:
1. Extract ALL financial line items with their values for 2024 and 2023
2. Categorize items into: shareholders_funds, non_current_liabilities, current_liabilities, non_current_assets, current_assets
3. Return ONLY a valid JSON response with this exact structure:

{
  "equity_and_liabilities": {
    "shareholders_funds": [
      {"label": "Share Capital", "note": "2", "value_2024": 542.52, "value_2023": 542.52}
    ],
    "non_current_liabilities": [...],
    "current_liabilities": [...]
  },
  "assets": {
    "non_current_assets": [...],
    "current_assets": [...]
  },
  "metadata": {
    "currency": "Lakhs",
    "date_2024": "March 31, 2024",
    "date_2023": "March 31, 2023"
  }
}

4. For each item, include: label, note (if available), value_2024, value_2023
5. Use 0.0 for missing values
6. Ensure ALL numerical values are properly converted to float
7. Do not include any text outside the JSON response"""
            },
            {
                "role": "user", 
                "content": f"Extract balance sheet data from this JSON:\n\n{json_str}"
            }
        ]
        
        try:
            response = self.call_openrouter_api(prompt_messages)
            
            # Clean and parse AI response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            extracted_data = json.loads(response)
            print("✅ AI successfully extracted financial data")
            return extracted_data
            
        except Exception as e:
            print(f"❌ AI extraction failed: {str(e)}")
            return self.fallback_manual_extraction(json_data)

    def fallback_manual_extraction(self, json_data: Dict) -> Dict:
        """Fallback manual extraction when AI fails."""
        print("🔄 Using fallback manual extraction...")
        
        extracted_data = {
            "equity_and_liabilities": {
                "shareholders_funds": [],
                "non_current_liabilities": [],
                "current_liabilities": []
            },
            "assets": {
                "non_current_assets": [],
                "current_assets": []
            },
            "metadata": {
                "currency": "Lakhs",
                "date_2024": "March 31, 2024",
                "date_2023": "March 31, 2023"
            }
        }
        
        def search_and_categorize(data, path=""):
            """Recursively search for financial data."""
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and any(year in str(value) for year in ['2024', '2023']):
                        # Try to extract financial values
                        label = str(key).replace('_', ' ').title()
                        
                        # Look for 2024 and 2023 values
                        value_2024 = 0.0
                        value_2023 = 0.0
                        note = ""
                        
                        if 'Value_2024' in value:
                            value_2024 = self.safe_float_conversion(value['Value_2024'])
                        if 'Value_2023' in value:
                            value_2023 = self.safe_float_conversion(value['Value_2023'])
                        
                        if value_2024 != 0.0 or value_2023 != 0.0:
                            # Categorize based on keywords
                            item = {
                                "label": label,
                                "note": note,
                                "value_2024": value_2024,
                                "value_2023": value_2023
                            }
                            
                            label_lower = label.lower()
                            
                            # Categorization logic
                            if any(keyword in label_lower for keyword in self.balance_sheet_structure["equity_and_liabilities"]["shareholders_funds"]):
                                extracted_data["equity_and_liabilities"]["shareholders_funds"].append(item)
                            elif any(keyword in label_lower for keyword in self.balance_sheet_structure["equity_and_liabilities"]["non_current_liabilities"]):
                                extracted_data["equity_and_liabilities"]["non_current_liabilities"].append(item)
                            elif any(keyword in label_lower for keyword in self.balance_sheet_structure["equity_and_liabilities"]["current_liabilities"]):
                                extracted_data["equity_and_liabilities"]["current_liabilities"].append(item)
                            elif any(keyword in label_lower for keyword in self.balance_sheet_structure["assets"]["non_current_assets"]):
                                extracted_data["assets"]["non_current_assets"].append(item)
                            elif any(keyword in label_lower for keyword in self.balance_sheet_structure["assets"]["current_assets"]):
                                extracted_data["assets"]["current_assets"].append(item)
                    else:
                        search_and_categorize(value, f"{path}.{key}")
                        
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    search_and_categorize(item, f"{path}[{i}]")
        
        search_and_categorize(json_data)
        return extracted_data

    def generate_balance_sheet_excel(self, financial_data: Dict, output_dir: str = "output") -> str:
        """Generate Excel balance sheet from extracted financial data."""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Balance Sheet"
        
        # Define styles
        title_font = Font(bold=True, size=12)
        header_font = Font(bold=True, size=10)
        section_font = Font(bold=True, size=10)
        normal_font = Font(size=10)
        total_font = Font(bold=True, size=10)
        footer_font = Font(size=9)
        
        # Borders
        thin_border = Border(
            left=Side(style="thin"), right=Side(style="thin"),
            top=Side(style="thin"), bottom=Side(style="thin")
        )
        top_border = Border(top=Side(style="thin"))
        bottom_border = Border(bottom=Side(style="thin"))
        double_bottom_border = Border(bottom=Side(style="double"))
        
        # Alignments
        center_align = Alignment(horizontal="center", vertical="center")
        left_align = Alignment(horizontal="left", vertical="center")
        right_align = Alignment(horizontal="right", vertical="center")
        
        # Set column widths to match template
        ws.column_dimensions["A"].width = 35  # Description
        ws.column_dimensions["B"].width = 10  # Notes
        ws.column_dimensions["C"].width = 18  # As at March 31, 2024
        ws.column_dimensions["D"].width = 18  # As at March 31, 2023
        
        row = 1
        
        # Title
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        ws.cell(row=row, column=1).value = "Consolidated Balance Sheet"
        ws.cell(row=row, column=1).font = title_font
        ws.cell(row=row, column=1).alignment = center_align
        row += 2
        
        # Currency header
        ws.cell(row=row, column=4).value = f"In {financial_data['metadata']['currency']}"
        ws.cell(row=row, column=4).font = normal_font
        ws.cell(row=row, column=4).alignment = right_align
        row += 1
        
        # Column headers
        ws.cell(row=row, column=2).value = "Note No."
        ws.cell(row=row, column=3).value = "As at March 31, 2024"
        ws.cell(row=row, column=4).value = "As at March 31, 2023"
        
        for col in ['B', 'C', 'D']:
            ws[f"{col}{row}"].font = header_font
            ws[f"{col}{row}"].alignment = center_align
            ws[f"{col}{row}"].border = bottom_border
        row += 1
        
        def add_data_row(description: str, note: str, val_2024: float, val_2023: float, 
                        is_bold: bool = False, is_section: bool = False, is_total: bool = False, 
                        is_grand_total: bool = False, indent_level: int = 0):
            """Add a data row with proper formatting to match template."""
            nonlocal row
            
            # Description with proper indentation
            cell_a = ws.cell(row=row, column=1)
            if indent_level > 0:
                cell_a.value = "    " * indent_level + description
            else:
                cell_a.value = description
                
            if is_section:
                cell_a.font = section_font
            elif is_bold or is_total or is_grand_total:
                cell_a.font = total_font
            else:
                cell_a.font = normal_font
            cell_a.alignment = left_align
            
            # Note
            cell_b = ws.cell(row=row, column=2)
            cell_b.value = note if note else ""
            cell_b.font = normal_font
            cell_b.alignment = center_align
            
            # 2024 value
            cell_c = ws.cell(row=row, column=3)
            if val_2024 != 0:
                cell_c.value = val_2024
                cell_c.number_format = '#,##0.00'
            cell_c.font = total_font if (is_bold or is_total or is_grand_total) else normal_font
            cell_c.alignment = right_align
            
            # Add borders for totals
            if is_total:
                cell_c.border = top_border
            elif is_grand_total:
                cell_c.border = double_bottom_border
            
            # 2023 value
            cell_d = ws.cell(row=row, column=4)
            if val_2023 != 0:
                cell_d.value = val_2023
                cell_d.number_format = '#,##0.00'
            cell_d.font = total_font if (is_bold or is_total or is_grand_total) else normal_font
            cell_d.alignment = right_align
            
            # Add borders for totals
            if is_total:
                cell_d.border = top_border
            elif is_grand_total:
                cell_d.border = double_bottom_border
            
            row += 1
        
        # EQUITY AND LIABILITIES SECTION
        add_data_row("EQUITY AND LIABILITIES", "", 0, 0, is_section=True)
        
        # Shareholders' funds
        add_data_row("Equity", "", 0, 0, is_section=True, indent_level=1)
        shareholders_total_2024 = 0
        shareholders_total_2023 = 0
        
        for item in financial_data["equity_and_liabilities"]["shareholders_funds"]:
            add_data_row(item["label"], item["note"], item["value_2024"], item["value_2023"], indent_level=2)
            shareholders_total_2024 += item["value_2024"]
            shareholders_total_2023 += item["value_2023"]
        
        # Shareholders' funds total
        add_data_row("Total Equity", "", shareholders_total_2024, shareholders_total_2023, is_total=True, indent_level=1)
        
        # Non-Current liabilities
        if financial_data["equity_and_liabilities"]["non_current_liabilities"]:
            add_data_row("Non-Current Liabilities", "", 0, 0, is_section=True, indent_level=1)
            non_current_total_2024 = 0
            non_current_total_2023 = 0
            
            for item in financial_data["equity_and_liabilities"]["non_current_liabilities"]:
                add_data_row(item["label"], item["note"], item["value_2024"], item["value_2023"], indent_level=2)
                non_current_total_2024 += item["value_2024"]
                non_current_total_2023 += item["value_2023"]
            
            # Non-current liabilities total
            add_data_row("Total Non-Current Liabilities", "", non_current_total_2024, non_current_total_2023, is_total=True, indent_level=1)
        else:
            non_current_total_2024 = 0
            non_current_total_2023 = 0
        
        # Current liabilities
        add_data_row("Current Liabilities", "", 0, 0, is_section=True, indent_level=1)
        current_liab_total_2024 = 0
        current_liab_total_2023 = 0
        
        for item in financial_data["equity_and_liabilities"]["current_liabilities"]:
            add_data_row(item["label"], item["note"], item["value_2024"], item["value_2023"], indent_level=2)
            current_liab_total_2024 += item["value_2024"]
            current_liab_total_2023 += item["value_2023"]
        
        # Current liabilities total
        add_data_row("Total Current Liabilities", "", current_liab_total_2024, current_liab_total_2023, is_total=True, indent_level=1)
        
        # TOTAL EQUITY AND LIABILITIES
        total_eq_liab_2024 = shareholders_total_2024 + non_current_total_2024 + current_liab_total_2024
        total_eq_liab_2023 = shareholders_total_2023 + non_current_total_2023 + current_liab_total_2023
        add_data_row("TOTAL", "", total_eq_liab_2024, total_eq_liab_2023, is_grand_total=True)
        
        # Empty row
        row += 1
        
        # ASSETS SECTION
        add_data_row("ASSETS", "", 0, 0, is_section=True)
        
        # Non-current assets
        add_data_row("Non-Current Assets", "", 0, 0, is_section=True, indent_level=1)
        non_current_assets_total_2024 = 0
        non_current_assets_total_2023 = 0
        
        # Check if we have subcategories for non-current assets
        fixed_assets_items = []
        other_non_current_items = []
        
        for item in financial_data["assets"]["non_current_assets"]:
            label_lower = item["label"].lower()
            if any(keyword in label_lower for keyword in ["fixed", "tangible", "intangible", "plant", "equipment", "building", "land"]):
                fixed_assets_items.append(item)
            else:
                other_non_current_items.append(item)
        
        # Fixed assets subsection if we have fixed asset items
        if fixed_assets_items:
            add_data_row("Property, Plant and Equipment", "", 0, 0, is_section=True, indent_level=2)
            fixed_assets_2024 = 0
            fixed_assets_2023 = 0
            
            for item in fixed_assets_items:
                add_data_row(item["label"], item["note"], item["value_2024"], item["value_2023"], indent_level=3)
                fixed_assets_2024 += item["value_2024"]
                fixed_assets_2023 += item["value_2023"]
            
            non_current_assets_total_2024 += fixed_assets_2024
            non_current_assets_total_2023 += fixed_assets_2023
        
        # Other non-current assets
        for item in other_non_current_items:
            add_data_row(item["label"], item["note"], item["value_2024"], item["value_2023"], indent_level=2)
            non_current_assets_total_2024 += item["value_2024"]
            non_current_assets_total_2023 += item["value_2023"]
        
        # Non-current assets total
        add_data_row("Total Non-Current Assets", "", non_current_assets_total_2024, non_current_assets_total_2023, is_total=True, indent_level=1)
        
        # Current assets
        add_data_row("Current Assets", "", 0, 0, is_section=True, indent_level=1)
        current_assets_total_2024 = 0
        current_assets_total_2023 = 0
        
        for item in financial_data["assets"]["current_assets"]:
            add_data_row(item["label"], item["note"], item["value_2024"], item["value_2023"], indent_level=2)
            current_assets_total_2024 += item["value_2024"]
            current_assets_total_2023 += item["value_2023"]
        
        # Current assets total
        add_data_row("Total Current Assets", "", current_assets_total_2024, current_assets_total_2023, is_total=True, indent_level=1)
        
        # TOTAL ASSETS
        total_assets_2024 = non_current_assets_total_2024 + current_assets_total_2024
        total_assets_2023 = non_current_assets_total_2023 + current_assets_total_2023
        add_data_row("TOTAL", "", total_assets_2024, total_assets_2023, is_grand_total=True)
        
        # Footer notes
        row += 1
        
        # Note about accompanying notes
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        ws.cell(row=row, column=1).value = "The accompanying notes form an integral part of these financial statements."
        ws.cell(row=row, column=1).font = footer_font
        ws.cell(row=row, column=1).alignment = left_align
        row += 1
        
        # Date and signature section
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        ws.cell(row=row, column=1).value = "As per our report of even date"
        ws.cell(row=row, column=1).font = footer_font
        ws.cell(row=row, column=1).alignment = center_align
        row += 1
        
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        ws.cell(row=row, column=1).value = "For [Auditor Firm Name]"
        ws.cell(row=row, column=1).font = footer_font
        ws.cell(row=row, column=1).alignment = left_align
        
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        ws.cell(row=row, column=3).value = "For and on behalf of the Board of Directors"
        ws.cell(row=row, column=3).font = footer_font
        ws.cell(row=row, column=3).alignment = right_align
        row += 1
        
        # Auditor signature
        ws.cell(row=row, column=1).value = "Signature"
        ws.cell(row=row, column=1).font = footer_font
        ws.cell(row=row, column=1).alignment = left_align
        
        ws.cell(row=row, column=4).value = "Director"
        ws.cell(row=row, column=4).font = footer_font
        ws.cell(row=row, column=4).alignment = right_align
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"balance_sheet_{timestamp}.xlsx")
        
        try:
            wb.save(output_file)
            print(f"✅ Balance Sheet generated: {output_file}")
            
            # Print summary
            print("\n" + "="*60)
            print("📊 BALANCE SHEET SUMMARY")
            print("="*60)
            print(f"Total Assets 2024:           ₹{total_assets_2024:>12,.2f} {financial_data['metadata']['currency']}")
            print(f"Total Assets 2023:           ₹{total_assets_2023:>12,.2f} {financial_data['metadata']['currency']}")
            print(f"Total Equity & Liab 2024:    ₹{total_eq_liab_2024:>12,.2f} {financial_data['metadata']['currency']}")
            print(f"Total Equity & Liab 2023:    ₹{total_eq_liab_2023:>12,.2f} {financial_data['metadata']['currency']}")
            print(f"Balance Check 2024:          {'✅ BALANCED' if abs(total_assets_2024 - total_eq_liab_2024) < 0.01 else '❌ NOT BALANCED'}")
            print(f"Balance Check 2023:          {'✅ BALANCED' if abs(total_assets_2023 - total_eq_liab_2023) < 0.01 else '❌ NOT BALANCED'}")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")
            return None

    def process_json_file(self, input_file: str, output_dir: str = "output") -> str:
        """Main method to process JSON file and generate balance sheet."""
        try:
            # Load JSON data
            print(f"📂 Loading JSON file: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print("✅ JSON file loaded successfully")
            
            # Extract financial data using AI
            print("🤖 Extracting financial data with AI...")
            financial_data = self.extract_financial_data_with_ai(json_data)
            
            # Generate Excel balance sheet
            print("📊 Generating Excel balance sheet...")
            output_file = self.generate_balance_sheet_excel(financial_data, output_dir)
            
            if output_file:
                print(f"\n🎉 Balance Sheet generation completed!")
                print(f"📁 Output file: {output_file}")
                return output_file
            else:
                raise Exception("Failed to generate Excel file")
                
        except Exception as e:
            print(f"❌ Error processing file: {str(e)}")
            return None

def main():
    """Main function to run the balance sheet generator."""
    print("🚀 FLEXIBLE BALANCE SHEET GENERATOR")
    print("=" * 50)
    
    # Get configuration from environment variables
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    INPUT_FILE = os.getenv("INPUT_FILE", "output/ai_enhanced_data.json")  # Default fallback
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")  # Default fallback
    
    # Check if API key is provided
    if not OPENROUTER_API_KEY:
        print("❌ OpenRouter API key not found in environment variables")
        print("Please add OPENROUTER_API_KEY to your .env file")
        print("Get your API key from: https://openrouter.ai/")
        return
    
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("Please ensure the input file exists or update INPUT_FILE in your .env file")
        return
    
    # Initialize generator
    generator = BalanceSheetGenerator(OPENROUTER_API_KEY)
    
    # Process the file
    result = generator.process_json_file(INPUT_FILE, OUTPUT_DIR)
    
    if result:
        print("\n✅ Process completed successfully!")
    else:
        print("\n❌ Process failed!")

if __name__ == "__main__":
    main()