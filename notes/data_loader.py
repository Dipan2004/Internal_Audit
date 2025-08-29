import os
import json
import logging
import pandas as pd
from typing import Any
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings
from utils.utils import clean_value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
	"""Application settings loaded from environment variables or .env file."""
	trial_balance_json: str = "data/output1/parsed_trial_balance.json"

settings = Settings()

class TrialBalanceRecord(BaseModel):
	account_name: str
	amount: float
	group: str

def load_trial_balance() -> pd.DataFrame:
	"""
	Load trial balance data from a JSON file, validate with Pydantic, and return as a cleaned DataFrame.
	Raises FileNotFoundError if the file does not exist.
	"""
	json_file = settings.trial_balance_json
	if not os.path.exists(json_file):
		logger.error(f"{json_file} not found! Please run the data extraction step first.")
		raise FileNotFoundError(f"{json_file} not found! Please run the data extraction step first.")

	with open(json_file, "r", encoding="utf-8") as f:
		parsed_data = json.load(f)

	# Determine the structure and load into DataFrame
	if isinstance(parsed_data, list):
		records = parsed_data
	else:
		records = parsed_data.get("trial_balance", parsed_data)

	validated_records = []
	for record in records:
		try:
			validated = TrialBalanceRecord(**record)
			validated_dict = validated.dict()
		except ValidationError as ve:
			logger.warning(f"Validation error for record: {ve}")
			validated_dict = record  # fallback to raw dict
		validated_records.append(validated_dict)

	tb_df = pd.DataFrame(validated_records)
	tb_df['amount'] = tb_df['amount'].apply(clean_value)
	logger.info(f"Loaded trial balance with {len(tb_df)} records.")
	return tb_df
