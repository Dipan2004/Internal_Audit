import re
import json
import os
import requests
from typing import Dict, List, Any, Optional
import pandas as pd
from collections import defaultdict
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or manually set environment variables")

class EnhancedDataExtractor:
    def __init__(self, openrouter_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Dynamic patterns for trash detection
        self.dynamic_trash_indicators = [
            r'^Unnamed:\s*\d*$',  # Unnamed columns
            r'^\s*$',  # Empty strings
            r'^#NAME\?$',  # Excel errors
            r'^\d{8,}$',  # Long timestamp-like numbers
            r'^[Dd]ifference$',  # Difference labels
            r'^\.\.\.$',  # Ellipsis
            r'^-+$',  # Dash lines
            r'^=+$',  # Equal lines
        ]
        
        # Configurable thresholds
        self.min_section_items = 1
        self.max_empty_ratio = 0.8  # Max 80% empty cells in a row
        
    def call_mistral_api(self, prompt: str, data_sample: str) -> Dict[str, Any]:
        """Call OpenRouter Mistral 8x7B model for data analysis"""
        if not self.openrouter_api_key:
            return {"error": "OpenRouter API key not provided"}
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are a financial data analysis expert. Your task is to analyze and structure financial data from various formats (CSV, text, tables). 

Key responsibilities:
1. Identify financial sections (Share Capital, Reserves, Borrowings, etc.)
2. Extract numerical values with proper formatting
3. Recognize date patterns and financial periods
4. Structure hierarchical data (main items, sub-items, details)
5. Handle currency symbols, percentages, and financial notation
6. Identify relationships between data points
7. Clean and standardize financial terminology

Return your analysis as structured JSON with:
- Clear section identification
- Properly parsed numerical values
- Date/period information
- Hierarchical structure where applicable
- Data quality indicators
- Key insights or anomalies found

Be precise with numbers and maintain financial accuracy."""

        user_prompt = f"""{prompt}

Please analyze this financial data and provide a structured JSON response:

{data_sample}

Focus on:
1. Identifying all financial sections and subsections
2. Extracting all numerical values with proper context
3. Recognizing financial periods and dates
4. Creating a logical hierarchy of information
5. Flagging any data quality issues or anomalies
6. Providing summary insights"""

        payload = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4000,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(self.openrouter_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON blocks in the response
                    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        # Try to find JSON without code blocks
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group(0))
                        else:
                            return {"analysis": content, "format": "text"}
                except json.JSONDecodeError:
                    return {"analysis": content, "format": "text", "parse_error": True}
            
            return {"error": "No response from API"}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def is_likely_trash(self, value: Any) -> bool:
        """Dynamically determine if a value is likely trash"""
        if value is None or pd.isna(value):
            return True
            
        str_val = str(value).strip()
        if not str_val:
            return True
            
        # Check against dynamic patterns
        for pattern in self.dynamic_trash_indicators:
            if re.match(pattern, str_val, re.IGNORECASE):
                return True
                
        return False
    
    def detect_numeric_value(self, value: str) -> Optional[float]:
        """Intelligently detect and clean numeric values"""
        if not value or self.is_likely_trash(value):
            return None
            
        # Clean common formatting
        cleaned = str(value).strip()
        
        # Handle parentheses as negative
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Remove common separators
        cleaned = re.sub(r'[,\s]', '', cleaned)
        
        # Try to extract number
        number_match = re.search(r'[-+]?\d*\.?\d+', cleaned)
        if number_match:
            try:
                return float(number_match.group())
            except ValueError:
                pass
                
        return None
    
    def detect_date_pattern(self, text: str) -> List[str]:
        """Dynamically detect date patterns"""
        date_patterns = [
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{4}/\d{2}/\d{2}',
            r'\d{2}\.\d{2}\.\d{4}',
            r'\w+\s+\d{1,2},?\s+\d{4}',  # Month Day, Year
        ]
        
        found_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            found_dates.extend(matches)
            
        return found_dates
    
    def identify_section_headers(self, lines: List[str]) -> Dict[int, str]:
        """Dynamically identify section headers"""
        section_headers = {}
        
        for i, line in enumerate(lines):
            if not line or self.is_likely_trash(line):
                continue
                
            line = line.strip()
            
            # Look for numbered sections (1. 2. 3. etc.)
            numbered_section = re.match(r'^(\d+)\.\s*(.+)', line)
            if numbered_section:
                section_headers[i] = numbered_section.group(2).strip()
                continue
            
            # Look for lines that seem like headers (short, descriptive)
            if (len(line.split()) <= 10 and 
                not any(char.isdigit() for char in line.split()[-1]) and
                len(line) > 5):
                # Check if next few lines contain data
                has_data_following = False
                for j in range(i+1, min(i+5, len(lines))):
                    if self.detect_numeric_value(lines[j]):
                        has_data_following = True
                        break
                
                if has_data_following:
                    section_headers[i] = line
        
        return section_headers
    
    def parse_tabular_data(self, lines: List[str], start_idx: int, end_idx: int) -> Dict[str, Any]:
        """Parse tabular data between start and end indices - enhanced for financial data"""
        if start_idx >= end_idx:
            return {}
            
        relevant_lines = lines[start_idx:end_idx]
        
        # Split lines into columns, prioritizing tab delimiter for financial data
        rows = []
        max_cols = 0
        
        for line in relevant_lines:
            if not line or self.is_likely_trash(line):
                continue
            
            # For financial data, tabs are most common, then multiple spaces
            best_split = []
            
            # Try tab delimiter first (most common in financial exports)
            if '\t' in line:
                cols = [col.strip() for col in line.split('\t')]
                best_split = [col for col in cols if col]  # Keep empty cells for alignment
            else:
                # Try multiple spaces
                cols = re.split(r'\s{2,}', line.strip())
                best_split = [col.strip() for col in cols if col.strip()]
            
            if best_split:
                rows.append(best_split)
                max_cols = max(max_cols, len(best_split))
        
        if not rows:
            return {}
        
        # Enhanced header and data identification for financial data
        headers = []
        data_rows = []
        dates_found = []
        
        for i, row in enumerate(rows):
            # Skip rows that are mostly empty
            non_empty_count = sum(1 for cell in row if cell and not self.is_likely_trash(cell))
            if non_empty_count == 0:
                continue
            
            # Look for date patterns in this row
            row_dates = []
            for cell in row:
                row_dates.extend(self.detect_date_pattern(str(cell)))
            dates_found.extend(row_dates)
            
            # Check if row contains financial amounts
            numeric_count = sum(1 for cell in row if self.detect_numeric_value(cell) is not None)
            
            # If row has dates, it might be a header row
            if row_dates and not headers:
                headers = row
            # If row is mostly numeric, it's likely a data row
            elif numeric_count > 0:
                data_rows.append(row)
            # If no headers yet and row has descriptive text, it might be headers
            elif not headers and any(len(str(cell)) > 3 for cell in row):
                headers = row
        
        # Structure the data
        structured_data = {
            'headers': headers,
            'data': [],
            'dates': list(set(dates_found)),  # Remove duplicates
            'metadata': {
                'total_rows': len(data_rows),
                'columns': max_cols,
                'header_row_found': bool(headers)
            }
        }
        
        # Process data rows with enhanced financial data handling
        for row in data_rows:
            if not row:
                continue
                
            # Find the best identifier (usually first non-empty cell)
            row_name = None
            values_start_idx = 0
            
            for idx, cell in enumerate(row):
                if cell and not self.is_likely_trash(cell) and not self.detect_numeric_value(cell):
                    row_name = str(cell).strip()
                    values_start_idx = idx + 1
                    break
            
            if not row_name and row:
                # If no text identifier, use first cell as name
                row_name = str(row[0]).strip() if row[0] else f"row_{len(structured_data['data'])}"
                values_start_idx = 1
            
            # Extract values from remaining cells
            row_values = {}
            for j, cell in enumerate(row[values_start_idx:], values_start_idx):
                if not cell:
                    continue
                    
                numeric_val = self.detect_numeric_value(cell)
                if numeric_val is not None:
                    # Use header if available, otherwise create column name
                    if j < len(headers) and headers[j]:
                        col_key = str(headers[j]).strip()
                    else:
                        col_key = f'column_{j}'
                    row_values[col_key] = numeric_val
                elif not self.is_likely_trash(cell):
                    if j < len(headers) and headers[j]:
                        col_key = str(headers[j]).strip()
                    else:
                        col_key = f'column_{j}'
                    row_values[col_key] = str(cell).strip()
            
            # Only add if has meaningful data
            if row_name and row_values:
                structured_data['data'].append({
                    'name': row_name,
                    'values': row_values
                })
        
        return structured_data
    
    def detect_hierarchical_structure(self, data: List[Dict]) -> Dict[str, Any]:
        """Detect and create hierarchical structure from flat data"""
        hierarchy = defaultdict(list)
        
        for item in data:
            name = item.get('name', '')
            
            # Look for indentation or sub-item indicators
            if name.startswith(('  ', '\t')):  # Indented = sub-item
                parent_key = 'sub_items'
                item['name'] = name.strip()
                hierarchy[parent_key].append(item)
            elif any(indicator in name.lower() for indicator in ['(a)', '(b)', '(c)', 'add:', 'less:']):
                hierarchy['details'].append(item)
            else:
                hierarchy['main_items'].append(item)
        
        return dict(hierarchy)
    
    def extract_structured_data(self, input_data: str, use_ai_analysis: bool = True) -> Dict[str, Any]:
        """Main extraction method with AI enhancement"""
        lines = [line.strip() for line in input_data.strip().split('\n')]
        
        # Remove completely empty lines
        lines = [line for line in lines if line]
        
        if not lines:
            return {'error': 'No data found'}
        
        # Get AI analysis first if enabled
        ai_analysis = {}
        if use_ai_analysis and self.openrouter_api_key:
            # Limit data sample for API call (first 3000 chars)
            data_sample = input_data[:3000] + "..." if len(input_data) > 3000 else input_data
            
            prompt = """Analyze this financial data and provide structured insights. Focus on:
1. Identifying financial statement sections
2. Extracting key numerical values
3. Understanding the data structure and relationships
4. Flagging any anomalies or important patterns"""
            
            ai_analysis = self.call_mistral_api(prompt, data_sample)
        
        # Continue with existing logic
        section_headers = self.identify_section_headers(lines)
        
        result = {
            'metadata': {
                'extraction_timestamp': pd.Timestamp.now().isoformat(),
                'total_lines': len(lines),
                'sections_found': len(section_headers),
                'ai_analysis_enabled': use_ai_analysis and bool(self.openrouter_api_key)
            },
            'sections': {},
            'ai_insights': ai_analysis if ai_analysis else None
        }
        
        # If no clear sections found, treat as single data block
        if not section_headers:
            single_section = self.parse_tabular_data(lines, 0, len(lines))
            if single_section:
                result['sections']['main_data'] = single_section
            return result
        
        # Process each section
        section_indices = sorted(section_headers.keys())
        
        for i, section_start in enumerate(section_indices):
            section_name = section_headers[section_start]
            section_end = section_indices[i + 1] if i + 1 < len(section_indices) else len(lines)
            
            # Parse section data
            section_data = self.parse_tabular_data(lines, section_start + 1, section_end)
            
            if section_data and section_data.get('data'):
                # Add hierarchical structure detection
                hierarchical_data = self.detect_hierarchical_structure(section_data['data'])
                section_data['structure'] = hierarchical_data
                
                # Clean section name for JSON key
                clean_section_name = re.sub(r'[^\w\s]', '', section_name).strip().lower().replace(' ', '_')
                result['sections'][clean_section_name] = section_data
        
        return result

def process_folder_with_ai(input_folder: str = "csv_notes", 
                          output_file: str = "output/ai_enhanced_data.json",
                          openrouter_api_key: str = None):
    """Process all files in folder with AI enhancement"""
    
    input_path = Path(input_folder)
    output_path = Path(output_file)
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if input folder exists
    if not input_path.exists():
        print(f"Error: Input folder '{input_folder}' does not exist!")
        return
    
    # Get all files
    supported_extensions = ['.txt', '.csv', '.tsv', '.dat', '.log']
    files = []
    
    for ext in supported_extensions:
        files.extend(input_path.glob(f'*{ext}'))
    
    # Also get files without extensions
    for file in input_path.iterdir():
        if file.is_file() and not file.suffix:
            files.append(file)
    
    if not files:
        print(f"No files found in '{input_folder}'")
        return
    
    print(f"Found {len(files)} files to process...")
    
    # Initialize enhanced extractor
    extractor = EnhancedDataExtractor(openrouter_api_key)
    
    # Combined result
    combined_data = {
        'processing_info': {
            'total_files': len(files),
            'processed_files': [],
            'failed_files': [],
            'extraction_timestamp': pd.Timestamp.now().isoformat(),
            'ai_enhanced': bool(openrouter_api_key)
        },
        'files': {}
    }
    
    # Process each file
    for file_path in files:
        try:
            print(f"Processing {file_path.name}...")
            
            # Read file with encoding detection
            content = None
            for encoding in ['utf-8', 'utf-16', 'latin1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if not content:
                print(f"Could not read {file_path.name}")
                combined_data['processing_info']['failed_files'].append(file_path.name)
                continue
            
            # Extract structured data with AI analysis
            structured_data = extractor.extract_structured_data(content, use_ai_analysis=True)
            
            # Add to combined result
            file_key = file_path.stem  # filename without extension
            combined_data['files'][file_key] = {
                'source_file': file_path.name,
                'file_size': file_path.stat().st_size,
                'data': structured_data
            }
            
            combined_data['processing_info']['processed_files'].append(file_path.name)
            print(f"✓ Successfully processed {file_path.name}")
            
        except Exception as e:
            print(f"✗ Error processing {file_path.name}: {str(e)}")
            combined_data['processing_info']['failed_files'].append(file_path.name)
    
    # Save combined JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✓ AI-enhanced data saved to: {output_file}")
    print(f"Successfully processed: {len(combined_data['processing_info']['processed_files'])} files")
    print(f"Failed: {len(combined_data['processing_info']['failed_files'])} files")
    
    return combined_data

# Example usage
if __name__ == "__main__":
    # Try to get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    print("🔑 API Key Status:")
    if api_key:
        print(f"   ✓ Found API key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
    else:
        print("   ❌ No API key found in environment")
        print("   Check your .env file contains: OPENROUTER_API_KEY=your_key_here")
        print("   Or run: export OPENROUTER_API_KEY='your_key_here'")
    print()
    
    if not api_key:
        print("🤖 AI Analysis: DISABLED (no API key)")
        print("📊 Basic extraction will still work\n")
    else:
        print("🤖 AI Analysis: ENABLED")
        print("📊 Advanced financial analysis available\n")
    
    # Process sample data from the second document
    sample_data = """2. Share capital				In Lakhs			
			31-03-2024 00:00	31-03-2023 00:00			
Authorised shares							
75,70,000 (March 31, 2024 : 75,70,000) equity shares of ₹ 10/- each			757	757			
Issued, subscribed and fully paid-up shares							
54,25,210 (March 31, 2024 : 54,25,210) equity shares of ₹ 10/- each			542.521	542.521			
Total issued, subscribed and fully paid-up share capital			542.521	542.521			
(a) Reconciliation of the equity shares outstanding at the beginning and at the end of the year							
	31-03-2024 00:00		31-03-2023 00:00				
	No's	Amount	No's	Amount			
Equity shares of ₹ 10/- each fully paid							
At the beginning of the year	54.2521	543	54.2521	543			
Outstanding at the end of the year	54.2521	543	54.2521	543"""
    
    # Initialize extractor
    extractor = EnhancedDataExtractor(api_key)
    
    print("🔄 Processing sample financial data...")
    
    # Extract with AI analysis (will fallback gracefully if no API key)
    result = extractor.extract_structured_data(sample_data, use_ai_analysis=bool(api_key))
    
    print("=" * 60)
    print("FINANCIAL DATA EXTRACTION RESULTS")
    print("=" * 60)
    
    # Print metadata
    print(f"📊 Total lines processed: {result['metadata']['total_lines']}")
    print(f"📑 Sections found: {result['metadata']['sections_found']}")
    print(f"🤖 AI analysis: {'Enabled' if result['metadata']['ai_analysis_enabled'] else 'Disabled'}")
    print()
    
    # Print sections
    if result.get('sections'):
        for section_name, section_data in result['sections'].items():
            print(f"📋 SECTION: {section_name.replace('_', ' ').title()}")
            print(f"   - Rows: {section_data['metadata']['total_rows']}")
            print(f"   - Columns: {section_data['metadata']['columns']}")
            
            if section_data.get('dates'):
                print(f"   - Dates found: {section_data['dates']}")
            
            # Show some sample data
            if section_data.get('data'):
                print("   - Sample data:")
                for item in section_data['data'][:3]:  # Show first 3 items
                    print(f"     • {item['name']}: {item['values']}")
            print()
    
    # Print AI insights if available
    if result.get('ai_insights'):
        if 'error' in result['ai_insights']:
            print(f"⚠️  AI Analysis Error: {result['ai_insights']['error']}")
            if 'Unauthorized' in str(result['ai_insights']['error']):
                print("   → Check if your API key is valid and has credits")
                print("   → Verify key format: sk-or-v1-...")
        else:
            print("🤖 AI INSIGHTS:")
            if isinstance(result['ai_insights'], dict):
                print(json.dumps(result['ai_insights'], indent=2))
            else:
                print(result['ai_insights'])
    
    print("\n" + "=" * 60)
    
    # NOW PROCESS ACTUAL FILES AND SAVE OUTPUT
    print("🔄 Now processing files from folder and saving output...")
    print("=" * 60)
    
    # This is the fix - actually call the function to process files and save output
    processed_data = process_folder_with_ai("csv_notes", "output/ai_enhanced_data.json", api_key)
    
    print("=" * 60)
    print("💡 TIPS:")
    print("• JSON output saved to: output/ai_enhanced_data.json")
    print("• To change input folder, modify 'csv_notes' parameter")
    print("• To change output file, modify 'output/ai_enhanced_data.json' parameter")
    print("• Check .env file format: OPENROUTER_API_KEY=your_key_here")
    print("=" * 60)
    
    # Debugging: Show environment variables (comment out in production)
    print(f"\n🔍 DEBUG INFO:")
    print(f"   Environment variables loaded: {len([k for k in os.environ.keys() if 'OPENROUTER' in k])}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   .env file exists: {os.path.exists('.env')}")
    
    if processed_data:
        print(f"   Files processed: {len(processed_data['processing_info']['processed_files'])}")
        print(f"   Files failed: {len(processed_data['processing_info']['failed_files'])}")
    else:
        print("   No files were processed (check if csv_notes folder exists)")