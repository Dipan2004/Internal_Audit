import logging
from typing import Any, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_value(value: Union[str, float, int, None]) -> float:
	"""
	Clean and convert a value to float.
	Removes commas from strings and strips whitespace.
	Returns 0.0 if conversion fails.
	"""
	try:
		if isinstance(value, str):
			value = value.replace(',', '').strip()
		return float(value) if value else 0.0
	except (ValueError, TypeError):
		logger.debug(f"Could not clean value: {value}")
		return 0.0

def to_lakhs(value: Union[float, int, str]) -> float:
	"""
	Convert a numeric value to lakhs (divide by 100,000 and round to 2 decimals).
	Accepts int, float, or numeric string.
	"""
	try:
		if isinstance(value, str):
			value = float(value.replace(',', '').strip())
		return round(float(value) / 100000, 2)
	except (ValueError, TypeError):
		logger.debug(f"Could not convert to lakhs: {value}")
		return 0.0

def convert_note_json_to_lakhs(note_json: Any) -> Any:
	"""
	Recursively convert all numeric values in a note JSON to lakhs.
	Returns the converted object.
	"""
	def convert(obj: Any) -> Any:
		if isinstance(obj, dict):
			for k, v in obj.items():
				if isinstance(v, (int, float)):
					obj[k] = to_lakhs(v)
				elif isinstance(v, str):
					try:
						obj[k] = to_lakhs(float(v.replace(',', '')))
					except Exception:
						obj[k] = v
				else:
					obj[k] = convert(v)
		elif isinstance(obj, list):
			for i in range(len(obj)):
				obj[i] = convert(obj[i])
		return obj

	return convert(note_json)
