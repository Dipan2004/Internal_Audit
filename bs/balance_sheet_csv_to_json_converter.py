import pandas as pd
import json
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Settings for CSV to JSON conversion, loaded from environment variables or .env file."""
    csv_folder_path: str = Field(default="data/csv_notes_bs", env="CSV_FOLDER_PATH")
    output_json: str = Field(default="data/clean_financial_data_bs.json", env="OUTPUT_JSON")

settings = Settings()

class NoteSection(BaseModel):
    title: str
    data: Dict[str, Any]

class FixedAssetData(BaseModel):
    gross_carrying_value: Dict[str, Optional[Union[float, int]]]
    accumulated_depreciation: Dict[str, Optional[Union[float, int]]]
    net_carrying_value: Dict[str, Optional[Union[float, int]]]

class FinancialData(BaseModel):
    processing_summary: Dict[str, Any]
    share_capital: Dict[str, Any] = Field(default_factory=dict)
    reserves_and_surplus: Dict[str, Any] = Field(default_factory=dict)
    borrowings: Dict[str, Any] = Field(default_factory=dict)
    current_liabilities: Dict[str, Any] = Field(default_factory=dict)
    fixed_assets: Dict[str, Any] = Field(default_factory=dict)
    current_assets: Dict[str, Any] = Field(default_factory=dict)
    loans_and_advances: Dict[str, Any] = Field(default_factory=dict)
    other_data: Dict[str, Any] = Field(default_factory=dict)

class FinancialCSVMapper:
    def __init__(self, csv_folder_path: str = settings.csv_folder_path):
        self.csv_folder_path = csv_folder_path

    def clean_value(self, value: Any) -> Optional[Union[float, int, str]]:
        """
        Clean and convert values appropriately.
        Returns None for empty or NaN values.
        """
        if pd.isna(value) or value == '':
            return None
        value_str = str(value).strip()
        cleaned_num = re.sub(r'[,\s₹]', '', value_str)
        try:
            if '.' in cleaned_num:
                return float(cleaned_num)
            else:
                return int(cleaned_num)
        except (ValueError, TypeError):
            return value_str

    def identify_note_sections(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Identify and extract note sections (e.g., 2. Share capital, 3. Reserves).
        Returns a dictionary of section title to parsed data.
        """
        sections = {}
        current_section = None
        current_data = []

        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
            # Check if this is a new section header (starts with number and dot)
            if re.match(r'^\d+\.?\s+[A-Za-z]', first_col):
                # Save previous section
                if current_section and current_data:
                    sections[current_section] = self.parse_section_data(current_data)
                
                # Start new section
                current_section = first_col.strip()
                current_data = []
            else:
                # Add row to current section
                if current_section:
                    row_data = [self.clean_value(cell) for cell in row]
                    if any(cell is not None for cell in row_data):  # Skip empty rows
                        current_data.append(row_data)
        
        # Handle last section
        if current_section and current_data:
            sections[current_section] = self.parse_section_data(current_data)
        
        return sections

    def parse_section_data(self, rows: List[List[Any]]) -> Dict:
        """
        Parse section data into a meaningful structure.
        Returns a dictionary mapping keys to values or date-mapped values.
        """
        if not rows:
            return {}
        
        section_data = {}
        
        # Find date headers (usually in first or second row)
        date_row = None
        for i, row in enumerate(rows[:3]):
            for cell in row:
                if cell and isinstance(cell, str) and re.search(r'\d{4}-\d{2}-\d{2}', str(cell)):
                    date_row = i
                    break
            if date_row is not None:
                break
        
        # Extract dates if found
        dates = []
        if date_row is not None:
            dates = [cell for cell in rows[date_row] if cell and re.search(r'\d{4}-\d{2}-\d{2}', str(cell))]
        
        # Process data rows
        for row in rows:
            if not row or not row[0]:
                continue
            
            key = str(row[0]).strip()
            
            # Skip header/date rows
            if date_row is not None and row == rows[date_row]:
                continue
            if any(date in str(cell) for cell in row for date in dates if date):
                continue
            
            # Extract values (non-None values after the key)
            values = [cell for cell in row[1:] if cell is not None]
            
            if values:
                if len(values) == 1:
                    section_data[key] = values[0]
                else:
                    # If we have dates, map values to dates
                    if dates and len(values) <= len(dates):
                        section_data[key] = {dates[i]: values[i] for i in range(len(values))}
                    else:
                        section_data[key] = values
        
        # Add dates to metadata if found
        if dates:
            section_data["_metadata"] = {"reporting_dates": dates}
        
        return section_data

    def parse_fixed_assets(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse fixed assets table (Note 9) with proper structure.
        Returns a dictionary with tangible, intangible, and totals.
        """
        fixed_assets = {
            "tangible_assets": {},
            "intangible_assets": {},
            "totals": {}
        }
        
        current_category = None
        
        for idx, row in df.iterrows():
            first_col = self.clean_value(row.iloc[0])
            
            # Skip header rows
            if not first_col or "Particulars" in str(first_col) or "Gross Carrying" in str(first_col):
                continue
            
            # Identify categories
            if "Tangible Assets" in str(first_col):
                current_category = "tangible"
                continue
            elif "Intangible Assets" in str(first_col):
                current_category = "intangible"
                continue
            elif "Total" in str(first_col) or "Grand Total" in str(first_col):
                current_category = "totals"
            
            # Extract asset data
            if current_category and len(row) > 1:
                asset_name = str(first_col).strip()
                
                # Remove numbering (1, 2, 3, etc.)
                asset_name = re.sub(r'^\d+\s*', '', asset_name)
                
                asset_data = FixedAssetData(
                    gross_carrying_value={
                        "opening": self.clean_value(row.iloc[2]) if len(row) > 2 else None,
                        "additions": self.clean_value(row.iloc[3]) if len(row) > 3 else None,
                        "deletions": self.clean_value(row.iloc[4]) if len(row) > 4 else None,
                        "closing": self.clean_value(row.iloc[5]) if len(row) > 5 else None
                    },
                    accumulated_depreciation={
                        "opening": self.clean_value(row.iloc[6]) if len(row) > 6 else None,
                        "for_the_year": self.clean_value(row.iloc[7]) if len(row) > 7 else None,
                        "deletions": self.clean_value(row.iloc[8]) if len(row) > 8 else None,
                        "closing": self.clean_value(row.iloc[9]) if len(row) > 9 else None
                    },
                    net_carrying_value={
                        "closing": self.clean_value(row.iloc[10]) if len(row) > 10 else None,
                        "opening": self.clean_value(row.iloc[11]) if len(row) > 11 else None
                    }
                )
                
                if current_category == "tangible":
                    fixed_assets["tangible_assets"][asset_name] = asset_data.dict()
                elif current_category == "intangible":
                    fixed_assets["intangible_assets"][asset_name] = asset_data.dict()
                elif current_category == "totals":
                    fixed_assets["totals"][asset_name] = asset_data.dict()
        
        return fixed_assets
    
    def parse_trade_receivables_aging(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse trade receivables aging analysis.
        Returns a dictionary of year to aging buckets.
        """
        aging_data = {}
        current_year = None
        
        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
            
            # Identify year sections
            if "2024" in first_col:
                current_year = "2024"
                continue
            elif "2023" in first_col:
                current_year = "2023"
                continue
            
            # Parse aging buckets
            if current_year and "Considered good" in first_col:
                aging_data[current_year] = {
                    "0_6_months": self.clean_value(row.iloc[1]) if len(row) > 1 else None,
                    "6_12_months": self.clean_value(row.iloc[2]) if len(row) > 2 else None,
                    "1_2_years": self.clean_value(row.iloc[3]) if len(row) > 3 else None,
                    "2_3_years": self.clean_value(row.iloc[4]) if len(row) > 4 else None,
                    "more_than_3_years": self.clean_value(row.iloc[5]) if len(row) > 5 else None,
                    "total": self.clean_value(row.iloc[6]) if len(row) > 6 else None
                }
        
        return aging_data
    
    def process_single_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single CSV file with intelligent parsing.
        Returns a dictionary of processed data.
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            filename = os.path.basename(file_path)
            result = {
                "file_name": filename,
                "processing_date": datetime.now().isoformat()
            }
            # Special handling for different note types
            if "Note_9" in filename:
                # Fixed assets
                result["fixed_assets"] = self.parse_fixed_assets(df)
            elif "Note_2_to_8" in filename or "Note_10_to_15" in filename:
                # Share capital, reserves, borrowings, etc.
                result["notes"] = self.identify_note_sections(df)
                
                # Special handling for trade receivables aging
                if any("Age wise analysis" in str(cell) for row in df.values for cell in row):
                    result["trade_receivables_aging"] = self.parse_trade_receivables_aging(df)
            else:
                # Generic note parsing
                result["notes"] = self.identify_note_sections(df)
            
            return result
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {
                "file_name": os.path.basename(file_path),
                "error": str(e),
                "processing_date": datetime.now().isoformat()
            }
    
    def process_all_csvs(self) -> Dict[str, Any]:
        """
        Process all CSV files and create meaningful financial JSON.
        Returns the structured financial data.
        """
        if not os.path.exists(self.csv_folder_path):
            logger.error(f"Folder {self.csv_folder_path} not found")
            return {"error": f"Folder {self.csv_folder_path} not found"}
        
        csv_files = [f for f in os.listdir(self.csv_folder_path) if f.endswith('.csv')]
        
        if not csv_files:
            logger.error(f"No CSV files found in {self.csv_folder_path}")
            return {"error": f"No CSV files found in {self.csv_folder_path}"}
        
        financial_data = FinancialData(
            processing_summary={
                "total_files": len(csv_files),
                "processing_date": datetime.now().isoformat(),
                "processed_files": []
            }
        )
        
        # Process each file
        for csv_file in csv_files:
            file_path = os.path.join(self.csv_folder_path, csv_file)
            file_data = self.process_single_csv(file_path)
            
            if "error" not in file_data:
                financial_data.processing_summary["processed_files"].append(csv_file)
                
                # Organize data by financial statement categories
                if "notes" in file_data:
                    for note_title, note_data in file_data["notes"].items():
                        if "Share capital" in note_title:
                            financial_data.share_capital = note_data
                        elif "Reserves and surplus" in note_title:
                            financial_data.reserves_and_surplus = note_data
                        elif "borrowings" in note_title.lower():
                            financial_data.borrowings[note_title] = note_data
                        elif any(x in note_title.lower() for x in ["payables", "liabilities", "provisions"]):
                            financial_data.current_liabilities[note_title] = note_data
                        elif any(x in note_title.lower() for x in ["receivables", "cash", "inventories"]):
                            financial_data.current_assets[note_title] = note_data
                        elif any(x in note_title.lower() for x in ["loans", "advances"]):
                            financial_data.loans_and_advances[note_title] = note_data
                        else:
                            financial_data.other_data[note_title] = note_data
                
                if "fixed_assets" in file_data:
                    financial_data.fixed_assets = file_data["fixed_assets"]
                
                if "trade_receivables_aging" in file_data:
                    financial_data.current_assets["trade_receivables_aging"] = file_data["trade_receivables_aging"]
        
        return {"company_financial_data": financial_data.dict()}
    
    def save_to_json(self, output_path: str = settings.output_json) -> str:
        """
        Process all CSVs and save meaningful financial JSON.
        Returns the output file path.
        """
        financial_data = self.process_all_csvs()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Clean financial JSON created: {output_path}")
        return output_path

# Usage
if __name__ == "__main__":
    mapper = FinancialCSVMapper(settings.csv_folder_path)
    output_file = mapper.save_to_json(settings.output_json)
    logger.info(f"Clean financial JSON created: {output_file}")