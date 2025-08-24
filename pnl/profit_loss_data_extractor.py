import os
import pandas as pd
import logging
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Settings for P&L CSV extraction, loaded from environment variables or .env file."""
    excel_file_path: str = Field(default="smaple0.xlsx", env="PNL_EXCEL_FILE_PATH")
    output_folder: str = Field(default="data/csv_notes_pnl", env="PNL_OUTPUT_FOLDER")
    note_16_23_sheet: str = Field(default="Note 16-23", env="PNL_NOTE_16_23_SHEET")
    skiprows: int = Field(default=3, env="PNL_SKIPROWS")

settings = Settings()

def get_xls(excel_file_path: str) -> pd.ExcelFile:
    try:
        xls = pd.ExcelFile(excel_file_path)
        logger.info(f"Loaded Excel file: {excel_file_path}")
        logger.info(f"Available sheets: {xls.sheet_names}")
        return xls
    except Exception as e:
        logger.error(f"Failed to load Excel file '{excel_file_path}': {e}")
        raise

class NoteCSVInfo(BaseModel):
    name: str
    rows: int

def clean_note(xls, sheet_name: str, skiprows: int = settings.skiprows) -> pd.DataFrame:
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
    # Always use absolute path for output folder
    abs_output_folder = os.path.abspath(output_folder)
    try:
        os.makedirs(abs_output_folder, exist_ok=True)
        logger.info(f"Output folder ensured: {abs_output_folder}")
    except Exception as e:
        logger.error(f"Failed to create output folder '{abs_output_folder}': {e}")
        raise
    output_path = os.path.join(abs_output_folder, filename)
    df.to_csv(output_path, index=False)
    logger.info(f"CSV file written to: {output_path}")
    return NoteCSVInfo(name=filename, rows=df.shape[0])

def main() -> None:
    """
    Main function to extract P&L notes from Excel and export as CSV.
    """
    import sys
    logger.info(f"Current working directory: {os.getcwd()}")
    excel_file_path = settings.excel_file_path
    if len(sys.argv) > 1:
        excel_file_path = sys.argv[1]
        logger.info(f"Excel file path from argument: {excel_file_path}")
    xls = get_xls(excel_file_path)
    if settings.note_16_23_sheet not in xls.sheet_names:
        logger.error(f"Sheet '{settings.note_16_23_sheet}' not found in Excel file. Available sheets: {xls.sheet_names}")
        return
    note_16_23_df = clean_note(xls, settings.note_16_23_sheet, settings.skiprows)
    logger.info(f"Loaded DataFrame shape: {note_16_23_df.shape}")
    logger.info(f"First few rows:\n{note_16_23_df.head()}\n")
    info_16_23 = export_note_to_csv(note_16_23_df, "Note_16_to_23_Full.csv", settings.output_folder)
    logger.info(f"Extracted rows: Note 16-23 = {info_16_23.rows} rows")
    abs_output_folder = os.path.abspath(settings.output_folder)
    logger.info(f"CSV output path: {os.path.join(abs_output_folder, 'Note_16_to_23_Full.csv')}")

if __name__ == "__main__":
    main()
