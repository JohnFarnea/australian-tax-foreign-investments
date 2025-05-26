"""
RBA exchange rate fetching and currency conversion utilities.
"""
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional


class RBAExchangeRates:
    """
    Class for fetching and processing RBA exchange rates.
    
    Note: Currently using hardcoded exchange rates as a temporary solution
    due to challenges parsing the RBA CSV file format.
    """
    
    def __init__(self):
        """
        Initialize RBA exchange rates.
        """
        self.rates_data = None
        self.rba_url = "https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv"
        self.local_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "sample_data", "f11.1-data.csv")
        self.last_updated = None
        # Version marker to verify code loading
        self.version = "hardcoded-fallback-v1.0"
    
    def fetch_rates(self) -> Tuple[bool, str]:
        """
        Create a DataFrame with hardcoded exchange rates.
        This is a temporary solution until the CSV parsing issues are resolved.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            print(f"Using RBAExchangeRates version: {self.version}")
            
            # Create a DataFrame with hardcoded values for common currencies
            # Using realistic exchange rates for AUD to foreign currencies
            dates = pd.date_range(start='2023-01-01', end='2025-05-23')
            data = {
                'Date': dates,
                'USD': [0.67] * len(dates),  # $1 AUD = $0.67 USD
                'EUR': [0.62] * len(dates),  # $1 AUD = €0.62 EUR
                'JPY': [95.0] * len(dates),  # $1 AUD = ¥95 JPY
                'GBP': [0.53] * len(dates),  # $1 AUD = £0.53 GBP
            }
            
            self.rates_data = pd.DataFrame(data)
            self.last_updated = datetime.now()
            
            return True, ""
        
        except Exception as e:
            return False, f"Error creating exchange rates: {str(e)}"
    
    def get_rate(self, date: datetime, currency: str) -> Tuple[bool, str, float]:
        """
        Get exchange rate for a specific date and currency.
        
        Args:
            date: Date for exchange rate
            currency: Currency code (e.g., USD, EUR)
        
        Returns:
            Tuple of (success, error_message, rate)
        """
        if self.rates_data is None:
            success, error_msg = self.fetch_rates()
            if not success:
                return False, error_msg, 0.0
        
        if currency == 'AUD':
            return True, "", 1.0
        
        if currency not in self.rates_data.columns:
            return False, f"Currency {currency} not found in exchange rates", 0.0
        
        # Find the closest date on or before the requested date
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            closest_date = self.rates_data[self.rates_data['Date'] <= date_str]['Date'].max()
            
            if pd.isna(closest_date):
                # If no date is found, use the earliest available date
                closest_date = self.rates_data['Date'].min()
                if pd.isna(closest_date):
                    return False, f"No exchange rate data available", 0.0
            
            # Get the rate for the closest date
            rate_row = self.rates_data.loc[self.rates_data['Date'] == closest_date]
            if rate_row.empty:
                return False, f"No exchange rate found for {currency} on or before {date_str}", 0.0
            
            rate = rate_row[currency].values[0]
            
            if pd.isna(rate):
                return False, f"Exchange rate for {currency} on {closest_date} is not available", 0.0
            
            return True, "", float(rate)
        except Exception as e:
            return False, f"Error retrieving exchange rate: {str(e)}", 0.0
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str, 
                      date: datetime) -> Tuple[bool, str, float]:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date for exchange rate
        
        Returns:
            Tuple of (success, error_message, converted_amount)
        """
        if from_currency == to_currency:
            return True, "", amount
        
        # Convert from source currency to AUD
        if from_currency != 'AUD':
            success, error_msg, rate = self.get_rate(date, from_currency)
            if not success:
                return False, error_msg, 0.0
            
            # FIXED: Corrected currency conversion direction
            # RBA rates are expressed as AUD per foreign currency
            # To convert foreign currency to AUD, divide by the rate
            amount_aud = amount / rate
        else:
            amount_aud = amount
        
        # Convert from AUD to target currency
        if to_currency != 'AUD':
            success, error_msg, rate = self.get_rate(date, to_currency)
            if not success:
                return False, error_msg, 0.0
            
            # FIXED: Corrected currency conversion direction
            # RBA rates are expressed as AUD per foreign currency
            # To convert AUD to foreign currency, multiply by the rate
            converted_amount = amount_aud * rate
        else:
            converted_amount = amount_aud
        
        return True, "", converted_amount
