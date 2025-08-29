import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NormalizedNote(BaseModel):
	note_number: Optional[str]
	note_title: Optional[str]
	full_title: Optional[str]
	table_data: List[Dict[str, Any]]
	breakdown: Dict[str, Any] = {}
	matched_accounts: List[Any] = []
	total_amount: Optional[float] = None
	total_amount_lakhs: Optional[float] = None
	matched_accounts_count: Optional[int] = None
	comparative_data: Dict[str, Any] = {}
	notes_and_disclosures: List[str] = []
	markdown_content: Optional[str] = ""

def is_date_label(label: str) -> bool:
	"""Check if a label is a date string."""
	import re
	return bool(re.match(r"^(March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$", label)) \
		or bool(re.match(r"^\d{4}-\d{2}-\d{2}$", label))

def normalize_llm_note_json(llm_json: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Normalize a single LLM-generated note JSON to standard format.
	Returns a dict compatible with NormalizedNote.
	"""
	note_number = llm_json.get("note_number") or llm_json.get("metadata", {}).get("note_number", "")
	note_title = llm_json.get("note_title") or llm_json.get("title", "")
	full_title = llm_json.get("full_title") or (f"{note_number}. {note_title}" if note_number else note_title)

	table_data: List[Dict[str, Any]] = []

	if "structure" in llm_json and llm_json["structure"]:
		for item in llm_json["structure"]:
			if "subcategories" in item and item["subcategories"]:
				for sub in item["subcategories"]:
					label = sub.get("label", "")
					if not is_date_label(label):
						row = {
							"particulars": label,
							"current_year": sub.get("value", ""),
							"previous_year": sub.get("previous_value", "-"),
						}
						table_data.append(row)
			if "category" in item and ("total" in item or "previous_total" in item):
				row = {
					"particulars": f"Total {item.get('category', '')}",
					"current_year": item.get("total", ""),
					"previous_year": item.get("previous_total", "-"),
				}
				table_data.append(row)

	# Optionally, add a header row
