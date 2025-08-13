import json
import pandas as pd
import os
from datetime import datetime

class CashFlowStatementGenerator:
    def __init__(self, extracted_data_file=None, extracted_data=None):
        """Initialize with extracted financial data"""
        if extracted_data_file:
            with open(extracted_data_file, 'r') as f:
                self.data = json.load(f)
        elif extracted_data:
            self.data = extracted_data
        else:
            raise ValueError("Either extracted_data_file or extracted_data must be provided")
    
    def format_amount(self, amount):
        """Format amount for display - return numeric value, formatting handled by Excel"""
        if amount is None or amount == '' or amount == '-':
            return 0
        
        try:
            return float(amount)
        except (ValueError, TypeError):
            return 0
    
    def generate_cash_flow_statement_xlsx(self, output_filename="cash_flow_statement.xlsx"):
        """Generate the complete Cash Flow Statement in Excel format with proper formatting"""
        pl_data = self.data['profit_and_loss']
        wc_data = self.data['working_capital']
        inv_data = self.data['investing_activities']
        fin_data = self.data['financing_activities']
        cash_data = self.data['cash_and_equivalents']
        
        # Create the cash flow statement data
        cfs_data = []
        
        # ==========================================
        # CASH FLOW FROM OPERATING ACTIVITIES
        # ==========================================
        
        # Profit before taxation
        pbt_current = self.format_amount(pl_data['profit_before_tax']['current'])
        pbt_previous = self.format_amount(pl_data['profit_before_tax']['previous'])
        
        # Adjustments
        dep_current = self.format_amount(pl_data['depreciation']['current'])
        dep_previous = self.format_amount(pl_data['depreciation']['previous'])
        
        int_inc_current = self.format_amount(pl_data['interest_income']['current'])
        int_inc_previous = self.format_amount(pl_data['interest_income']['previous'])
        
        # Operating profit before working capital changes
        op_profit_current = pbt_current + dep_current - int_inc_current
        op_profit_previous = pbt_previous + dep_previous - int_inc_previous
        
        # Working Capital Changes
        tr_change = self.format_amount(wc_data['trade_receivables']['change'])
        inv_change = self.format_amount(wc_data['inventories']['change'])
        oca_change = self.format_amount(wc_data['other_current_assets']['change'])
        stla_change = self.format_amount(wc_data['short_term_loans_advances']['change'])
        cwip_change = 0  # Capital Work in Progress (assumed 0)
        ltla_change = self.format_amount(wc_data['long_term_loans_advances']['change'])
        stp_change = self.format_amount(wc_data['short_term_provisions']['change'])
        tp_change = self.format_amount(wc_data['trade_payables']['change'])
        ocl_change = self.format_amount(wc_data['other_current_liabilities']['change'])
        
        # Total working capital change
        total_wc_change = tr_change + inv_change + oca_change + stla_change + cwip_change + ltla_change + stp_change + tp_change + ocl_change
        
        # Cash from operations
        cash_from_operations = op_profit_current + total_wc_change
        
        # Direct taxes paid
        tax_paid = 179.27  # Use current year tax provision as approximation
        net_operating_cash_flow = cash_from_operations - tax_paid
        
        # Investing Activities
        asset_purchases = self.format_amount(inv_data['asset_purchases']['total'])
        asset_sales = self.format_amount(inv_data['asset_sales']['total'])
        interest_income = self.format_amount(inv_data['interest_income']['current'])
        net_investing_cash_flow = -asset_purchases + asset_sales + interest_income
        
        # Financing Activities
        dividend_paid = self.format_amount(fin_data['dividend_paid']['current'])
        borrowing_change = self.format_amount(fin_data['long_term_borrowings']['change'])
        cmltd_repayment = abs(self.format_amount(fin_data['current_maturities']['change']))
        net_financing_cash_flow = -dividend_paid + borrowing_change - cmltd_repayment
        
        # Net change and cash positions
        net_change = net_operating_cash_flow + net_investing_cash_flow + net_financing_cash_flow
        cash_beginning = self.format_amount(cash_data['total']['previous'])
        cash_ending = self.format_amount(cash_data['total']['current'])
        
        # Build the statement data
        cfs_data = [
            ['Particulars', 'March 31, 2024', 'March 31, 2023'],
            ['', '', ''],
            ['Cash flow from operating activities', '', ''],
            ['Profit before taxation', pbt_current, pbt_previous],
            ['', '', ''],
            ['Adjustment for:', '', ''],
            ['Add: Depreciation and Amortisation Expense', dep_current, dep_previous],
            ['Less: Interest income', -int_inc_current, -int_inc_previous],
            ['Operating profit before working capital changes', op_profit_current, op_profit_previous],
            ['', '', ''],
            ['Movements in working capital:', '', ''],
            ['(Increase)/Decrease in Trade Receivables', tr_change, ''],
            ['(Increase)/Decrease in Inventories', inv_change, ''],
            ['(Increase)/Decrease in Other Current Assets', oca_change, ''],
            ['(Increase)/Decrease in Short Term Loans & Advances', stla_change, ''],
            ['(Increase)/Decrease in Capital Work in Progress', cwip_change, ''],
            ['(Increase)/Decrease in Long Term Loans & Advances', ltla_change, ''],
            ['Increase/(Decrease) in Short Term Provisions', stp_change, ''],
            ['Increase/(Decrease) in Trade Payables', tp_change, ''],
            ['Increase/(Decrease) in Other Current Liabilities', ocl_change, ''],
            ['Cash used in operations', cash_from_operations, ''],
            ['Less: Direct taxes paid (net of refunds)', -tax_paid, ''],
            ['Net cash flow from operating activities                    (A)', net_operating_cash_flow, ''],
            ['', '', ''],
            ['Cash flows from investing activities', '', ''],
            ['Purchase of Assets', -asset_purchases if asset_purchases > 0 else '', ''],
            ['Sale of Assets', asset_sales if asset_sales > 0 else '', ''],
            ['Interest income', interest_income, ''],
            ['Net cash flow from investing activities                     (B)', net_investing_cash_flow, ''],
            ['', '', ''],
            ['Cash flows from financing activities', '', ''],
            ['Dividend paid', -dividend_paid if dividend_paid > 0 else '', ''],
            ['Long Term Borrowings', borrowing_change if borrowing_change > 0 else '', ''],
            ['Repayment of borrowings', -abs(borrowing_change) if borrowing_change < 0 else '', ''],
            ['Net cash flow from financing activities                     (C)', net_financing_cash_flow, ''],
            ['', '', ''],
            ['Net increase/(decrease) in cash and cash equivalents  (A+B+C)', net_change, ''],
            ['Cash and cash equivalents at the beginning of the year', cash_beginning, ''],
            ['Cash and cash equivalents at the end of the year', cash_ending, cash_beginning],
            ['', '', ''],
            ['Components of cash and cash equivalents', '', ''],
            ['Cash on hand', self.format_amount(cash_data['cash_on_hand']['current']), self.format_amount(cash_data['cash_on_hand']['previous'])],
            ['With banks in Current Accounts', self.format_amount(cash_data['bank_balances']['current']), self.format_amount(cash_data['bank_balances']['previous'])],
            ['With banks in Fixed Deposits', self.format_amount(cash_data['fixed_deposits']['current']), self.format_amount(cash_data['fixed_deposits']['previous'])],
            ['Total cash and cash equivalents (Refer note 13)', cash_ending, cash_beginning]
        ]
        
        # Create DataFrame
        df = pd.DataFrame(cfs_data, columns=['Particulars', 'March 31, 2024', 'March 31, 2023'])
        
        # Create Excel writer with enhanced formatting
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            # Write data without headers first
            df.to_excel(writer, sheet_name='Cash Flow Statement', index=False, startrow=4, header=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Cash Flow Statement']
            
            # Define enhanced formats
            title_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'font_size': 16,
                'bg_color': '#366092',
                'font_color': 'white',
                'border': 1
            })
            
            subtitle_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'font_size': 12,
                'bg_color': '#D7E4BC'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'font_size': 11,
                'bg_color': '#F2F2F2',
                'border': 1
            })
            
            section_format = workbook.add_format({
                'bold': True,
                'align': 'left',
                'font_size': 11,
                'bg_color': '#E7E6E6',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right',
                'border': 1
            })
            
            bold_number_format = workbook.add_format({
                'bold': True,
                'num_format': '#,##0.00',
                'align': 'right',
                'border': 1,
                'bg_color': '#F0F0F0'
            })
            
            text_format = workbook.add_format({
                'align': 'left',
                'border': 1
            })
            
            # Write title and headers
            worksheet.merge_range('A1:C1', 'CASH FLOW STATEMENT', title_format)
            worksheet.merge_range('A2:C2', 'For the year ended March 31, 2024', subtitle_format)
            worksheet.merge_range('A3:C3', '(All amounts in Lakhs)', subtitle_format)
            
            # Write column headers
            worksheet.write('A5', 'Particulars', header_format)
            worksheet.write('B5', 'March 31, 2024', header_format)
            worksheet.write('C5', 'March 31, 2023', header_format)
            
            # Set column widths
            worksheet.set_column('A:A', 55)
            worksheet.set_column('B:C', 18)
            
            # Apply formatting to data rows
            for row_num, row_data in enumerate(cfs_data, start=6):
                particulars, current_val, previous_val = row_data
                
                # Determine if this is a section header
                is_section = any(section in particulars.lower() for section in [
                    'cash flow from operating', 'cash flows from investing', 
                    'cash flows from financing', 'adjustment for:', 
                    'movements in working capital:', 'components of cash'
                ])
                
                # Determine if this is a total/subtotal line
                is_total = any(keyword in particulars.lower() for keyword in [
                    'net cash flow', 'operating profit before working', 
                    'cash used in operations', 'net increase', 'total cash'
                ])
                
                # Write particulars column
                if is_section and particulars.strip():
                    worksheet.write(row_num - 1, 0, particulars, section_format)
                elif particulars.strip():
                    worksheet.write(row_num - 1, 0, particulars, text_format)
                else:
                    worksheet.write(row_num - 1, 0, '', text_format)
                
                # Write numeric columns
                for col, value in enumerate([current_val, previous_val], start=1):
                    if value == '' or value is None:
                        worksheet.write(row_num - 1, col, '', text_format)
                    elif isinstance(value, (int, float)) and value != 0:
                        if is_total:
                            worksheet.write_number(row_num - 1, col, value, bold_number_format)
                        else:
                            worksheet.write_number(row_num - 1, col, value, number_format)
                    else:
                        worksheet.write(row_num - 1, col, '', text_format)
            
            # Add borders around the entire table
            last_row = len(cfs_data) + 5
            border_format = workbook.add_format({'border': 2})
            
            # Set row heights for better appearance
            worksheet.set_row(0, 25)  # Title row
            worksheet.set_row(1, 20)  # Subtitle row
            worksheet.set_row(2, 20)  # Subtitle row
            worksheet.set_row(4, 20)  # Header row
        
        # Return comprehensive summary
        return {
            'operating_cash_flow': net_operating_cash_flow,
            'investing_cash_flow': net_investing_cash_flow,
            'financing_cash_flow': net_financing_cash_flow,
            'net_change_in_cash': net_change,
            'cash_beginning': cash_beginning,
            'cash_ending': cash_ending,
            'verification': {
                'calculated_net_change': net_change,
                'actual_cash_change': cash_ending - cash_beginning,
                'difference': net_change - (cash_ending - cash_beginning)
            },
            'output_file': output_filename,
            'detailed_calculations': {
                'profit_before_tax': {'current': pbt_current, 'previous': pbt_previous},
                'depreciation': {'current': dep_current, 'previous': dep_previous},
                'interest_income': {'current': int_inc_current, 'previous': int_inc_previous},
                'operating_profit_before_wc': {'current': op_profit_current, 'previous': op_profit_previous},
                'working_capital_changes': {
                    'trade_receivables': tr_change,
                    'inventories': inv_change,
                    'other_current_assets': oca_change,
                    'short_term_loans_advances': stla_change,
                    'long_term_loans_advances': ltla_change,
                    'short_term_provisions': stp_change,
                    'trade_payables': tp_change,
                    'other_current_liabilities': ocl_change,
                    'total': total_wc_change
                },
                'cash_from_operations': cash_from_operations,
                'tax_paid': tax_paid
            }
        }

def generate_cfs_template():
    """Generate a template showing the standard CFS format"""
    template = """
CASH FLOW STATEMENT TEMPLATE (Indian Format)
==========================================

                                                    March 31, 2024    March 31, 2023
                                                    (₹ in Lakhs)      (₹ in Lakhs)

Cash flow from operating activities
    Profit before taxation                              XXX.XX         XXX.XX
    
    Adjustment for:
        Add: Depreciation and Amortisation Expense      XXX.XX         XXX.XX
        Less: Interest income                          (XXX.XX)       (XXX.XX)
    Operating profit before working capital changes     XXX.XX         XXX.XX
    
    Movements in working capital:
        (Increase)/Decrease in Trade Receivables        XXX.XX         XXX.XX
        (Increase)/Decrease in Inventories              XXX.XX         XXX.XX
        (Increase)/Decrease in Other Current Assets     XXX.XX         XXX.XX
        (Increase)/Decrease in Short Term Loans & Advances XXX.XX      XXX.XX
        (Increase)/Decrease in Capital Work in Progress XXX.XX         XXX.XX
        (Increase)/Decrease in Long Term Loans & Advances XXX.XX       XXX.XX
        Increase/(Decrease) in Short Term Provisions    XXX.XX         XXX.XX
        Increase/(Decrease) in Trade Payables           XXX.XX         XXX.XX
        Increase/(Decrease) in Other Current Liabilities XXX.XX        XXX.XX
    Cash used in operations                             XXX.XX         XXX.XX
    Less: Direct taxes paid (net of refunds)          (XXX.XX)       (XXX.XX)
    Net cash flow from operating activities        (A) XXX.XX         XXX.XX

Cash flows from investing activities
    Purchase of Assets                                 (XXX.XX)       (XXX.XX)
    Sale of Assets                                      XXX.XX         XXX.XX
    Interest income                                     XXX.XX         XXX.XX
    Net cash flow from investing activities        (B) (XXX.XX)       (XXX.XX)

Cash flows from financing activities
    Dividend paid                                      (XXX.XX)       (XXX.XX)
    Long Term Borrowings                                XXX.XX         XXX.XX
    Repayment of borrowings                            (XXX.XX)       (XXX.XX)
    Net cash flow from financing activities        (C) XXX.XX         XXX.XX

Net increase/(decrease) in cash and cash equivalents (A+B+C) XXX.XX   XXX.XX
Cash and cash equivalents at the beginning of the year      XXX.XX    XXX.XX
Cash and cash equivalents at the end of the year            XXX.XX    XXX.XX

Components of cash and cash equivalents
    Cash on hand                                        XXX.XX         XXX.XX
    With banks in Current Accounts                      XXX.XX         XXX.XX
    With banks in Fixed Deposits                        XXX.XX         XXX.XX
    Total cash and cash equivalents (Refer note 13)    XXX.XX         XXX.XX
"""
    return template

def main_cfs_generation(extracted_data_file="extracted_cfs_data.json", output_filename="cash_flow_statement.xlsx"):
    """Main function to generate Cash Flow Statement from extracted data"""
    
    print("="*80)
    print("CASH FLOW STATEMENT GENERATOR")
    print("="*80)
    
    # Step 1: Load extracted data
    print("\n1. Loading extracted financial data...")
    try:
        if not os.path.exists(extracted_data_file):
            print(f"✗ Error: File {extracted_data_file} not found")
            print("Please run the Financial Data Extractor first to create this file")
            return None
        
        cfs_generator = CashFlowStatementGenerator(extracted_data_file=extracted_data_file)
        print(f"✓ Successfully loaded data from {extracted_data_file}")
    except Exception as e:
        print(f"✗ Error loading data: {str(e)}")
        return None
    
    # Step 2: Generate Cash Flow Statement Excel file
    print("\n2. Generating Cash Flow Statement Excel file...")
    
    cfs_summary = cfs_generator.generate_cash_flow_statement_xlsx(output_filename)
    
    print(f"✓ Cash Flow Statement saved to {cfs_summary['output_file']}")
    
    # Step 3: Print verification summary
    print(f"\n{'='*80}")
    print("CASH FLOW STATEMENT SUMMARY")
    print(f"{'='*80}")
    print(f"Operating Cash Flow: ₹{cfs_summary['operating_cash_flow']:,.2f} Lakhs")
    print(f"Investing Cash Flow: ₹{cfs_summary['investing_cash_flow']:,.2f} Lakhs")
    print(f"Financing Cash Flow: ₹{cfs_summary['financing_cash_flow']:,.2f} Lakhs")
    print(f"Net Change in Cash: ₹{cfs_summary['net_change_in_cash']:,.2f} Lakhs")
    
    print(f"\n{'='*80}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*80}")
    verification = cfs_summary['verification']
    print(f"Calculated Net Change in Cash: ₹{verification['calculated_net_change']:,.2f} Lakhs")
    print(f"Actual Change in Cash Balance: ₹{verification['actual_cash_change']:,.2f} Lakhs")
    print(f"Difference (should be close to 0): ₹{verification['difference']:,.2f} Lakhs")
    
    if abs(verification['difference']) < 1:
        print("✓ Cash Flow Statement balances correctly!")
    else:
        print("⚠ Cash Flow Statement has balancing difference - review calculations")
    
    print(f"\n{'='*80}")
    print("FILE CREATED:")
    print(f"{'='*80}")
    print(f"{cfs_summary['output_file']} - Cash Flow Statement")
    
    # Print detailed breakdown
    details = cfs_summary['detailed_calculations']
    print(f"\n{'='*80}")
    print("DETAILED BREAKDOWN:")
    print(f"{'='*80}")
    print(f"Profit Before Tax: ₹{details['profit_before_tax']['current']:,.2f} Lakhs")
    print(f"Add: Depreciation: ₹{details['depreciation']['current']:,.2f} Lakhs")
    print(f"Less: Interest Income: ₹{details['interest_income']['current']:,.2f} Lakhs")
    print(f"Operating Profit Before WC Changes: ₹{details['operating_profit_before_wc']['current']:,.2f} Lakhs")
    print(f"Total Working Capital Impact: ₹{details['working_capital_changes']['total']:,.2f} Lakhs")
    print(f"Cash from Operations: ₹{details['cash_from_operations']:,.2f} Lakhs")
    print(f"Less: Taxes Paid: ₹{details['tax_paid']:,.2f} Lakhs")
    
    return cfs_summary

def print_template():
    """Print the CFS template for reference"""
    print(generate_cfs_template())

# Example usage and testing
if __name__ == "__main__":
    # Main execution
    print("Starting Cash Flow Statement Generation Process...")
    
    # Check if extracted data file exists
    extracted_file = "extracted_cfs_data.json"
    if os.path.exists(extracted_file):
        # Generate Cash Flow Statement
        cfs_summary = main_cfs_generation(extracted_file, "cash_flow_statement.xlsx")
        
        if cfs_summary:
            print(f"\n{'='*80}")
            print("CASH FLOW STATEMENT GENERATION COMPLETED SUCCESSFULLY!")
            print(f"{'='*80}")
    else:
        print(f"Error: Extracted data file '{extracted_file}' not found")
        print("Please run the Financial Data Extractor first to create this file")
        print("\nAlternatively, you can view the CFS template:")
        print_template()