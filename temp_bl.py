class BalanceSheet:
    def __init__(self):
        self.equity_liabilities = {
            "Shareholders' funds": {
                "Share capital": {"note": "2", "2024": 0.0, "2023": 0.0},
                "Reserves and surplus": {"note": "3", "2024": 0.0, "2023": 0.0}
            },
            "Non-Current liabilities": {
                "Long term borrowings": {"note": "4", "2024": 0.0, "2023": 0.0},
                "Deferred Tax Liability (Net)": {"note": "5", "2024": 0.0, "2023": 0.0}
            },
            "Current liabilities": {
                "Trade payables": {"note": "6", "2024": 0.0, "2023": 0.0},
                "Other current liabilities": {"note": "7", "2024": 0.0, "2023": 0.0},
                "Short term provisions": {"note": "8", "2024": 0.0, "2023": 0.0}
            }
        }
        
        self.assets = {
            "Non-current assets": {
                "Fixed assets": {
                    "Tangible assets": {"note": "9", "2024": 0.0, "2023": 0.0},
                    "Intangible assets": {"note": "9", "2024": 0.0, "2023": 0.0}
                },
                "Capital Work in progress": {"note": "", "2024": 0.0, "2023": 0.0},
                "Long Term Loans and Advances": {"note": "10", "2024": 0.0, "2023": 0.0}
            },
            "Current assets": {
                "Inventories": {"note": "11", "2024": 0.0, "2023": 0.0},
                "Trade receivables": {"note": "12", "2024": 0.0, "2023": 0.0},
                "Cash and bank balances": {"note": "13", "2024": 0.0, "2023": 0.0},
                "Short-term loans and advances": {"note": "14", "2024": 0.0, "2023": 0.0},
                "Other current assets": {"note": "15", "2024": 0.0, "2023": 0.0}
            }
        }
        
        # Company information
        self.company_info = {
            "name": "Company Name",
            "year_end": "March 31, 2024",
            "currency": "In Lakhs",
            "auditor": "Auditor Name & Associates"
        }
    
    def set_company_info(self, name=None, year_end=None, currency=None, auditor=None):
        """Update company information"""
        if name: self.company_info["name"] = name
        if year_end: self.company_info["year_end"] = year_end
        if currency: self.company_info["currency"] = currency
        if auditor: self.company_info["auditor"] = auditor
    
    def update_item(self, section, category, item, note=None, val_2024=None, val_2023=None):
        """Update a specific balance sheet item"""
        try:
            if section == "equity_liabilities":
                target = self.equity_liabilities[category][item]
            elif section == "assets":
                if category == "Fixed assets":
                    target = self.assets["Non-current assets"]["Fixed assets"][item]
                else:
                    target = self.assets[category][item]
            else:
                return False
            
            if note is not None: target["note"] = str(note)
            if val_2024 is not None: target["2024"] = float(val_2024)
            if val_2023 is not None: target["2023"] = float(val_2023)
            return True
        except KeyError:
            return False
    
    def get_totals(self):
        """Calculate section totals"""
        totals = {}
        
        # Shareholders' funds total
        sf_2024 = sum(item["2024"] for item in self.equity_liabilities["Shareholders' funds"].values())
        sf_2023 = sum(item["2023"] for item in self.equity_liabilities["Shareholders' funds"].values())
        totals["shareholders_funds"] = {"2024": sf_2024, "2023": sf_2023}
        
        # Non-current liabilities total
        ncl_2024 = sum(item["2024"] for item in self.equity_liabilities["Non-Current liabilities"].values())
        ncl_2023 = sum(item["2023"] for item in self.equity_liabilities["Non-Current liabilities"].values())
        totals["non_current_liabilities"] = {"2024": ncl_2024, "2023": ncl_2023}
        
        # Current liabilities total
        cl_2024 = sum(item["2024"] for item in self.equity_liabilities["Current liabilities"].values())
        cl_2023 = sum(item["2023"] for item in self.equity_liabilities["Current liabilities"].values())
        totals["current_liabilities"] = {"2024": cl_2024, "2023": cl_2023}
        
        # Total equity and liabilities
        total_eq_liab_2024 = sf_2024 + ncl_2024 + cl_2024
        total_eq_liab_2023 = sf_2023 + ncl_2023 + cl_2023
        totals["total_equity_liabilities"] = {"2024": total_eq_liab_2024, "2023": total_eq_liab_2023}
        
        # Fixed assets total
        fa_2024 = sum(item["2024"] for item in self.assets["Non-current assets"]["Fixed assets"].values())
        fa_2023 = sum(item["2023"] for item in self.assets["Non-current assets"]["Fixed assets"].values())
        
        # Non-current assets total (including fixed assets)
        nca_other_2024 = (self.assets["Non-current assets"]["Capital Work in progress"]["2024"] + 
                         self.assets["Non-current assets"]["Long Term Loans and Advances"]["2024"])
        nca_other_2023 = (self.assets["Non-current assets"]["Capital Work in progress"]["2023"] + 
                         self.assets["Non-current assets"]["Long Term Loans and Advances"]["2023"])
        
        nca_2024 = fa_2024 + nca_other_2024
        nca_2023 = fa_2023 + nca_other_2023
        totals["non_current_assets"] = {"2024": nca_2024, "2023": nca_2023}
        
        # Current assets total
        ca_2024 = sum(item["2024"] for item in self.assets["Current assets"].values())
        ca_2023 = sum(item["2023"] for item in self.assets["Current assets"].values())
        totals["current_assets"] = {"2024": ca_2024, "2023": ca_2023}
        
        # Total assets
        total_assets_2024 = nca_2024 + ca_2024
        total_assets_2023 = nca_2023 + ca_2023
        totals["total_assets"] = {"2024": total_assets_2024, "2023": total_assets_2023}
        
        # Balance check
        totals["balanced"] = {
            "2024": abs(total_assets_2024 - total_eq_liab_2024) < 0.01,
            "2023": abs(total_assets_2023 - total_eq_liab_2023) < 0.01
        }
        
        return totals
    
    def validate_balance(self):
        """Check if balance sheet is balanced"""
        totals = self.get_totals()
        return totals["balanced"]["2024"] and totals["balanced"]["2023"]
    
    def to_dict(self):
        """Convert balance sheet to dictionary format"""
        return {
            "company_info": self.company_info,
            "equity_liabilities": self.equity_liabilities,
            "assets": self.assets,
            "totals": self.get_totals()
        }
    
    def from_dict(self, data):
        """Load balance sheet from dictionary"""
        if "company_info" in data:
            self.company_info.update(data["company_info"])
        if "equity_liabilities" in data:
            self.equity_liabilities = data["equity_liabilities"]
        if "assets" in data:
            self.assets = data["assets"]
    
    def print_summary(self):
        """Print a summary of the balance sheet"""
        totals = self.get_totals()
        print(f"\n{'='*50}")
        print(f"BALANCE SHEET SUMMARY - {self.company_info['year_end']}")
        print(f"{'='*50}")
        print(f"Currency: {self.company_info['currency']}")
        print(f"\nASSETS:")
        print(f"  Non-current assets: ₹{totals['non_current_assets']['2024']:,.2f}")
        print(f"  Current assets: ₹{totals['current_assets']['2024']:,.2f}")
        print(f"  TOTAL ASSETS: ₹{totals['total_assets']['2024']:,.2f}")
        print(f"\nEQUITY & LIABILITIES:")
        print(f"  Shareholders' funds: ₹{totals['shareholders_funds']['2024']:,.2f}")
        print(f"  Non-current liabilities: ₹{totals['non_current_liabilities']['2024']:,.2f}")
        print(f"  Current liabilities: ₹{totals['current_liabilities']['2024']:,.2f}")
        print(f"  TOTAL EQUITY & LIABILITIES: ₹{totals['total_equity_liabilities']['2024']:,.2f}")
        print(f"\nBALANCE CHECK: {'✅ BALANCED' if self.validate_balance() else '❌ NOT BALANCED'}")
        print(f"{'='*50}")

# Example usage and testing
if __name__ == "__main__":
    # Create a balance sheet instance
    bs = BalanceSheet()
    
    # Set company information
    bs.set_company_info(
        name="Siva Parvathi & Associates",
        year_end="March 31, 2024",
        currency="In Lakhs",
        auditor="M/s Siva Parvathi & Associates"
    )
    
    # Update some sample values (from your image)
    bs.update_item("equity_liabilities", "Shareholders' funds", "Share capital", "2", 542.52, 542.52)
    bs.update_item("equity_liabilities", "Shareholders' funds", "Reserves and surplus", "3", 3152.39, 2642.90)
    bs.update_item("equity_liabilities", "Non-Current liabilities", "Long term borrowings", "4", 914.46, 321.36)
    bs.update_item("equity_liabilities", "Non-Current liabilities", "Deferred Tax Liability (Net)", "5", 49.00, 43.19)
    bs.update_item("equity_liabilities", "Current liabilities", "Trade payables", "6", 147.01, 138.90)
    bs.update_item("equity_liabilities", "Current liabilities", "Other current liabilities", "7", 261.45, 344.12)
    bs.update_item("equity_liabilities", "Current liabilities", "Short term provisions", "8", 179.27, 692.25)
    
    bs.update_item("assets", "Non-current assets", "Tangible assets", "9", 3133.39, 1692.05)
    bs.update_item("assets", "Non-current assets", "Intangible assets", "9", 21.89, 6.06)
    bs.update_item("assets", "Capital Work in progress", "Capital Work in progress", "", 65.22, 0.0)
    bs.update_item("assets", "Long Term Loans and Advances", "Long Term Loans and Advances", "10", 81.81, 66.46)
    
    bs.update_item("assets", "Current assets", "Inventories", "11", 9.92, 10.13)
    bs.update_item("assets", "Current assets", "Trade receivables", "12", 833.79, 1037.70)
    bs.update_item("assets", "Current assets", "Cash and bank balances", "13", 595.11, 1122.45)
    bs.update_item("assets", "Current assets", "Short-term loans and advances", "14", 503.26, 789.27)
    bs.update_item("assets", "Current assets", "Other current assets", "15", 2.18, 1.01)
    
    # Print summary
    bs.print_summary()
    
    # Test individual functions
    share_capital = bs.equity_liabilities["Shareholders' funds"]["Share capital"]["2024"]
    print(f"\nShare Capital 2024: ₹{share_capital}")
    print(f"Is Balanced: {bs.validate_balance()}")