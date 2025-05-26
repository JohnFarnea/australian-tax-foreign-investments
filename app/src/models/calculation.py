"""
Tax calculation logic for Australian foreign investments.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

from utils.rba_rates import RBAExchangeRates


class TaxCalculator:
    """
    Class for calculating Australian tax liabilities on foreign share trading.
    """
    
    def __init__(self):
        self.rba_rates = RBAExchangeRates()
        self.opening_balance = None
        self.transactions = None
        self.results = {}
    
    def set_opening_balance(self, opening_balance_df: pd.DataFrame) -> None:
        """
        Set the opening balance data.
        
        Args:
            opening_balance_df: DataFrame containing opening balance data
        """
        self.opening_balance = opening_balance_df
    
    def set_transactions(self, transactions_df: pd.DataFrame) -> None:
        """
        Set the transactions data.
        
        Args:
            transactions_df: DataFrame containing transaction data
        """
        self.transactions = transactions_df
    
    def calculate_tax(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Calculate tax liability based on opening balance and transactions.
        
        Returns:
            Tuple of (success, error_message, results_dict)
        """
        if self.opening_balance is None:
            return False, "Opening balance data not provided", {}
        
        if self.transactions is None:
            return False, "Transaction data not provided", {}
        
        try:
            # Fetch RBA exchange rates
            success, error_msg = self.rba_rates.fetch_rates()
            if not success:
                return False, f"Failed to fetch exchange rates: {error_msg}", {}
            
            # Calculate closing balance
            closing_balance = self._calculate_closing_balance()
            
            # Calculate cost of shares sold
            cost_of_shares_sold = self._calculate_cost_of_shares_sold(closing_balance)
            
            # Calculate sales in AUD
            sales_aud, sales_details = self._calculate_sales_aud()
            
            # Calculate gross trading income
            gross_trading_income = sales_aud - cost_of_shares_sold
            
            # Prepare results
            self.results = {
                'opening_balance': self.opening_balance.to_dict('records'),
                'closing_balance': closing_balance.to_dict('records'),
                'cost_of_shares_sold': cost_of_shares_sold,
                'sales_aud': sales_aud,
                'gross_trading_income': gross_trading_income,
                'sales_details': sales_details,
                'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return True, "", self.results
            
        except Exception as e:
            return False, f"Error calculating tax: {str(e)}", {}
    
    def _calculate_closing_balance(self) -> pd.DataFrame:
        """
        Calculate closing balance based on opening balance and transactions.
        
        Returns:
            DataFrame containing closing balance
        """
        # Start with opening balance
        closing_balance = self.opening_balance.copy()
        
        # Group transactions by symbol
        grouped_transactions = self.transactions.groupby('Symbol')
        
        # Update quantities based on transactions
        for symbol, group in grouped_transactions:
            # Find the symbol in closing balance
            symbol_idx = closing_balance.index[closing_balance['Symbol'] == symbol].tolist()
            
            if symbol_idx:
                # Symbol exists in opening balance, update quantity
                idx = symbol_idx[0]
                net_quantity_change = group['Quantity'].sum()
                closing_balance.at[idx, 'Quantity'] += net_quantity_change
                
                # Update cost for purchases
                purchases = group[group['Quantity'] > 0]
                if not purchases.empty:
                    for _, row in purchases.iterrows():
                        # Convert purchase value to AUD if needed
                        if row['Currency'] != 'AUD':
                            success, _, rate = self.rba_rates.get_rate(
                                row['Date'], row['Currency']
                            )
                            if success:
                                purchase_value_aud = row['Net Value'] * rate
                            else:
                                # Fallback if rate not available
                                purchase_value_aud = row['Net Value']
                        else:
                            purchase_value_aud = row['Net Value']
                        
                        closing_balance.at[idx, 'Total Cost in AUD'] += purchase_value_aud
            else:
                # Symbol doesn't exist in opening balance, add new entry
                purchases = group[group['Quantity'] > 0]
                if not purchases.empty:
                    total_quantity = purchases['Quantity'].sum()
                    
                    # Calculate total cost in AUD
                    total_cost_aud = 0
                    for _, row in purchases.iterrows():
                        if row['Currency'] != 'AUD':
                            success, _, rate = self.rba_rates.get_rate(
                                row['Date'], row['Currency']
                            )
                            if success:
                                purchase_value_aud = row['Net Value'] * rate
                            else:
                                purchase_value_aud = row['Net Value']
                        else:
                            purchase_value_aud = row['Net Value']
                        
                        total_cost_aud += purchase_value_aud
                    
                    # Add new row to closing balance
                    new_row = pd.DataFrame({
                        'Symbol': [symbol],
                        'Quantity': [total_quantity],
                        'Total Cost in AUD': [total_cost_aud]
                    })
                    closing_balance = pd.concat([closing_balance, new_row], ignore_index=True)
        
        # Remove symbols with zero quantity
        closing_balance = closing_balance[closing_balance['Quantity'] > 0]
        
        return closing_balance
    
    def _calculate_cost_of_shares_sold(self, closing_balance: pd.DataFrame) -> float:
        """
        Calculate cost of shares sold.
        
        Formula: Cost of Shares Sold = Opening Balance + Purchases - Closing Balance
        
        Args:
            closing_balance: DataFrame containing closing balance
            
        Returns:
            Cost of shares sold in AUD
        """
        # Calculate total opening balance
        total_opening_balance = self.opening_balance['Total Cost in AUD'].sum()
        
        # Calculate total purchases
        purchases = self.transactions[self.transactions['Quantity'] > 0]
        total_purchases_aud = 0
        
        for _, row in purchases.iterrows():
            if row['Currency'] != 'AUD':
                success, _, rate = self.rba_rates.get_rate(row['Date'], row['Currency'])
                if success:
                    purchase_value_aud = row['Net Value'] * rate
                else:
                    purchase_value_aud = row['Net Value']
            else:
                purchase_value_aud = row['Net Value']
            
            total_purchases_aud += purchase_value_aud
        
        # Calculate total closing balance
        total_closing_balance = closing_balance['Total Cost in AUD'].sum()
        
        # Calculate cost of shares sold
        cost_of_shares_sold = total_opening_balance + total_purchases_aud - total_closing_balance
        
        return cost_of_shares_sold
    
    def _calculate_sales_aud(self) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate total sales in AUD and prepare detailed sales information.
        
        Returns:
            Tuple of (total_sales_aud, sales_details)
        """
        sales = self.transactions[self.transactions['Quantity'] < 0]
        total_sales_aud = 0
        sales_details = []
        
        for _, row in sales.iterrows():
            # Convert sale value to AUD if needed
            if row['Currency'] != 'AUD':
                success, _, rate = self.rba_rates.get_rate(row['Date'], row['Currency'])
                if success:
                    sale_value_aud = abs(row['Net Value']) * rate
                    exchange_rate = rate
                else:
                    sale_value_aud = abs(row['Net Value'])
                    exchange_rate = 1.0
            else:
                sale_value_aud = abs(row['Net Value'])
                exchange_rate = 1.0
            
            total_sales_aud += sale_value_aud
            
            # Add to sales details
            sales_details.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Symbol': row['Symbol'],
                'Quantity': abs(row['Quantity']),
                'Unit Price': row['Unit Price'],
                'Gross Value': abs(row['Total Gross Value']),
                'Commission': abs(row['Commission']),
                'Net Value': abs(row['Net Value']),
                'Currency': row['Currency'],
                'Exchange Rate': exchange_rate,
                'Value in AUD': sale_value_aud
            })
        
        return total_sales_aud, sales_details
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the calculation results.
        
        Returns:
            Dictionary containing calculation results
        """
        return self.results
