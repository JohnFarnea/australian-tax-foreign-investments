"""
Tax calculation logic for Australian foreign investments.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

from src.utils.rba_rates import RBAExchangeRates


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
        # FIXED: Opening balance is now optional
        if self.transactions is None:
            return False, "Transaction data not provided", {}
        
        try:
            # Fetch RBA exchange rates
            success, error_msg = self.rba_rates.fetch_rates()
            if not success:
                return False, f"Failed to fetch exchange rates: {error_msg}", {}
            
            # If no opening balance, create an empty DataFrame
            if self.opening_balance is None:
                self.opening_balance = pd.DataFrame(columns=['Symbol', 'Quantity', 'Total Cost in AUD'])
            
            # Process transactions and calculate tax
            closing_balance, cost_of_shares_sold, sales_aud, sales_details, purchases_details = self._process_transactions()
            
            # Calculate gross trading income
            gross_trading_income = sales_aud - cost_of_shares_sold
            
            # Calculate opening stock value (total cost from opening balance)
            opening_stock_value = self.opening_balance['Total Cost in AUD'].sum() if not self.opening_balance.empty else 0.0
            
            # Calculate closing stock value (total cost from closing balance)
            closing_stock_value = closing_balance['Total Cost in AUD'].sum() if not closing_balance.empty else 0.0
            
            # Calculate purchases value (opening stock + purchases - closing stock = cost of goods sold)
            purchases_value = cost_of_shares_sold + closing_stock_value - opening_stock_value
            
            # Prepare results
            self.results = {
                'opening_balance': self.opening_balance.to_dict('records'),
                'closing_balance': closing_balance.to_dict('records'),
                'cost_of_shares_sold': cost_of_shares_sold,
                'sales_aud': sales_aud,
                'gross_trading_income': gross_trading_income,
                'sales_details': sales_details,
                'purchases_details': purchases_details,
                'opening_stock_value': opening_stock_value,
                'closing_stock_value': closing_stock_value,
                'purchases_value': purchases_value,
                'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return True, "", self.results
            
        except Exception as e:
            return False, f"Error calculating tax: {str(e)}", {}
    
    def _process_transactions(self) -> Tuple[pd.DataFrame, float, float, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process all transactions and calculate closing balance, cost of shares sold, and sales in AUD.
        
        Returns:
            Tuple of (closing_balance_df, cost_of_shares_sold, sales_aud, sales_details, purchases_details)
        """
        # Initialize portfolio with opening balance
        portfolio = {}
        for _, row in self.opening_balance.iterrows():
            symbol = row['Symbol']
            quantity = row['Quantity']
            cost = row['Total Cost in AUD']
            
            if symbol not in portfolio:
                portfolio[symbol] = []
            
            # Add opening balance as a single lot
            portfolio[symbol].append({
                'quantity': quantity,
                'cost_per_share': cost / quantity if quantity > 0 else 0,
                'total_cost': cost
            })
        
        # Track cost of shares sold and sales in AUD
        cost_of_shares_sold = 0.0
        sales_aud = 0.0
        sales_details = []
        purchases_details = []
        
        # Process transactions in chronological order
        sorted_transactions = self.transactions.sort_values('Date')
        
        for _, row in sorted_transactions.iterrows():
            symbol = row['Symbol']
            quantity = row['Quantity']
            date = row['Date']
            
            # Ensure symbol exists in portfolio
            if symbol not in portfolio:
                portfolio[symbol] = []
            
            # Handle purchases
            if quantity > 0:
                # Convert purchase value to AUD
                if row['Currency'] != 'AUD':
                    success, _, rate = self.rba_rates.get_rate(date, row['Currency'])
                    if success:
                        # FIXED: Corrected currency conversion direction
                        purchase_value_aud = row['Net Value'] / rate
                        exchange_rate = rate
                    else:
                        purchase_value_aud = row['Net Value']
                        exchange_rate = 1.0
                else:
                    purchase_value_aud = row['Net Value']
                    exchange_rate = 1.0
                
                # Add new lot to portfolio
                portfolio[symbol].append({
                    'quantity': quantity,
                    'cost_per_share': purchase_value_aud / quantity,
                    'total_cost': purchase_value_aud
                })
                
                # Add to purchases details
                purchases_details.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Symbol': symbol,
                    'Quantity': quantity,
                    'Unit Price': row['Unit Price'],
                    'Gross Value': row['Total Gross Value'],
                    'Commission': abs(row['Commission']),
                    'Net Value': row['Net Value'],
                    'Currency': row['Currency'],
                    'Exchange Rate': exchange_rate,
                    'Value in AUD': purchase_value_aud
                })
            
            # Handle sales
            elif quantity < 0:
                quantity_to_sell = abs(quantity)
                sale_value_aud = 0.0
                
                # Convert sale value to AUD for reporting
                if row['Currency'] != 'AUD':
                    success, _, rate = self.rba_rates.get_rate(date, row['Currency'])
                    if success:
                        # FIXED: Corrected currency conversion direction
                        sale_value_aud = abs(row['Net Value']) / rate
                        exchange_rate = rate
                    else:
                        sale_value_aud = abs(row['Net Value'])
                        exchange_rate = 1.0
                else:
                    sale_value_aud = abs(row['Net Value'])
                    exchange_rate = 1.0
                
                # Add to total sales
                sales_aud += sale_value_aud
                
                # Add to sales details
                sales_details.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Symbol': symbol,
                    'Quantity': abs(quantity),
                    'Unit Price': row['Unit Price'],
                    'Gross Value': abs(row['Total Gross Value']),
                    'Commission': abs(row['Commission']),
                    'Net Value': abs(row['Net Value']),
                    'Currency': row['Currency'],
                    'Exchange Rate': exchange_rate,
                    'Value in AUD': sale_value_aud
                })
                
                # FIFO: Sell from oldest lots first
                lots_cost = 0.0
                remaining_to_sell = quantity_to_sell
                
                # Create a copy of the lots to avoid modifying during iteration
                lots = portfolio[symbol].copy()
                portfolio[symbol] = []
                
                for lot in lots:
                    if remaining_to_sell <= 0:
                        # No more shares to sell, keep the rest of the lot
                        portfolio[symbol].append(lot)
                    elif lot['quantity'] <= remaining_to_sell:
                        # Sell entire lot
                        lots_cost += lot['total_cost']
                        remaining_to_sell -= lot['quantity']
                    else:
                        # Sell part of the lot
                        sold_cost = lot['cost_per_share'] * remaining_to_sell
                        lots_cost += sold_cost
                        
                        # Keep the remaining shares in the lot
                        new_quantity = lot['quantity'] - remaining_to_sell
                        new_total_cost = lot['total_cost'] - sold_cost
                        
                        portfolio[symbol].append({
                            'quantity': new_quantity,
                            'cost_per_share': new_total_cost / new_quantity,
                            'total_cost': new_total_cost
                        })
                        
                        remaining_to_sell = 0
                
                # Add to cost of shares sold
                cost_of_shares_sold += lots_cost
        
        # Create closing balance DataFrame
        closing_balance_data = []
        for symbol, lots in portfolio.items():
            total_quantity = sum(lot['quantity'] for lot in lots)
            total_cost = sum(lot['total_cost'] for lot in lots)
            
            if total_quantity > 0:
                closing_balance_data.append({
                    'Symbol': symbol,
                    'Quantity': total_quantity,
                    'Total Cost in AUD': total_cost
                })
        
        closing_balance = pd.DataFrame(closing_balance_data)
        
        return closing_balance, cost_of_shares_sold, sales_aud, sales_details, purchases_details
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the calculation results.
        
        Returns:
            Dictionary containing calculation results
        """
        return self.results
