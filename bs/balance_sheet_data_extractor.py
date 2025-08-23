import os
import pandas as pd
import sys
import logging
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Ensure stdout encoding for Unicode
sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Settings for Balance Sheet CSV extraction, loaded from environment variables or .env file."""
    excel_file_path: str = Field(default="smaple0.xlsx", env="BS_EXCEL_FILE_PATH")
    output_folder: str = Field(default="data/csv_notes_bs", env="BS_OUTPUT_FOLDER")
    note_2_8_sheet: str = Field(default="Note 2 - 8", env="BS_NOTE_2_8_SHEET")
    note_9_sheet: str = Field(default="Note 9", env="BS_NOTE_9_SHEET")
    note_10_15_sheet: str = Field(default="Note 10-15", env="BS_NOTE_10_15_SHEET")
    skiprows: int = Field(default=3, env="BS_SKIPROWS")

settings = Settings()

class NoteCSVInfo(BaseModel):
    name: str
    rows: int

def clean_note(sheet_name: str, skiprows: int = settings.skiprows) -> pd.DataFrame:
    """
    Parse and clean a sheet from the Excel file.
    Drops empty rows and columns, resets index.
    """
    df = xls.parse(sheet_name, skiprows=skiprows)
    df = df.dropna(how='all').dropna(axis=1, how='all').reset_index(drop=True)
    return df

def export_note_to_csv(df: pd.DataFrame, filename: str, output_folder: str) -> NoteCSVInfo:
    """
    Export DataFrame to CSV and return info.
    """
    output_path = os.path.join(output_folder, filename)
    df.to_csv(output_path, index=False)
    return NoteCSVInfo(name=filename, rows=df.shape[0])

def main() -> None:
    """
    Main function to extract notes from Excel and export as CSVs.
    """
    # Use command-line argument for Excel file path if provided
    excel_path = settings.excel_file_path
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        logger.info(f"Excel file path from argument: {excel_path}")
    else:
        logger.info(f"Excel file path from settings: {excel_path}")
    global xls
    xls = pd.ExcelFile(excel_path)

    # Clean each sheet
    note_2_8_df = clean_note(settings.note_2_8_sheet, settings.skiprows)
    note_9_df = clean_note(settings.note_9_sheet, settings.skiprows)
    note_10_15_df = clean_note(settings.note_10_15_sheet, settings.skiprows)

    # Ensure output folder exists
    os.makedirs(settings.output_folder, exist_ok=True)

    # Export each as CSV in the folder
    info_2_8 = export_note_to_csv(note_2_8_df, "Note_2_to_8_Full.csv", settings.output_folder)
    info_9 = export_note_to_csv(note_9_df, "Note_9_Full.csv", settings.output_folder)
    info_10_15 = export_note_to_csv(note_10_15_df, "Note_10_to_15_Full.csv", settings.output_folder)

    # Log confirmation and row counts
    logger.info(f"Extracted rows: Note 2–8 = {info_2_8.rows} rows")
    logger.info(f"Extracted rows: Note 9   = {info_9.rows} rows")
    logger.info(f"Extracted rows: Note 10–15 = {info_10_15.rows} rows")

if __name__ == "__main__":
    main()
