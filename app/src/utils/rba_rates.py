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
    """
    
    def __init__(self, use_local_file=False):
        """
        Initialize RBA exchange rates.
        
        Args:
            use_local_file: Whether to use local sample file instead of fetching from RBA website
        """
        self.rates_df = None
        self.use_local_file = use_local_file
        self.rba_url = "https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv"
        self.local_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "sample_data", "f11.1-data.csv")
        
        # Map currency codes to RBA series IDs
        self.currency_to_series = {
            'USD': 'FXRUSD',
            'EUR': 'FXREUR',
            'JPY': 'FXRJPY',
            'GBP': 'FXRGBP',
            'CNY': 'FXRCNY',
            'HKD': 'FXRHKD',
            'SGD': 'FXRSGD',
            'CAD': 'FXRCAD',
            'NZD': 'FXRNZD'
        }
    
    def fetch_rates(self) -> Tuple[bool, str]:
        """
        Fetch exchange rates from RBA website or local file.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if self.use_local_file:
                # Use local sample file
                if not os.path.exists(self.local_file):
                    return False, f"Local file not found: {self.local_file}"
                
                # Read the CSV file with multiple header rows
                self.rates_df = pd.read_csv(self.local_file, skiprows=0)
                
                # Extract the currency codes from the second row
                header_row = pd.read_csv(self.local_file, nrows=1, skiprows=1).columns.tolist()
                
                # Create a mapping from column names to currency codes
                col_to_currency = {}
                for col in self.rates_df.columns[1:]:  # Skip the date column
                    for currency, series_id in self.currency_to_series.items():
                        if series_id in col:
                            col_to_currency[col] = currency
                
                # Rename columns to use currency codes
                rename_dict = {'Unnamed: 0': 'Date'}
                rename_dict.update(col_to_currency)
                self.rates_df = self.rates_df.rename(columns=rename_dict)
                
                # Convert date column to datetime
                self.rates_df['Date'] = pd.to_datetime(self.rates_df['Date'])
                
                return True, ""
            else:
                # Fetch from RBA website
                response = requests.get(self.rba_url)
                if response.status_code != 200:
                    return False, f"Failed to fetch RBA rates: HTTP {response.status_code}"
                
                # Save to temporary file and process
                temp_file = "temp_rba_rates.csv"
                with open(temp_file, "wb") as f:
                    f.write(response.content)
                
                # Read the CSV file with multiple header rows
                self.rates_df = pd.read_csv(temp_file, skiprows=0)
                
                # Extract the currency codes from the second row
                header_row = pd.read_csv(temp_file, nrows=1, skiprows=1).columns.tolist()
                
                # Create a mapping from column names to currency codes
                col_to_currency = {}
                for col in self.rates_df.columns[1:]:  # Skip the date column
                    for currency, series_id in self.currency_to_series.items():
                        if series_id in col:
                            col_to_currency[col] = currency
                
                # Rename columns to use currency codes
                rename_dict = {'Unnamed: 0': 'Date'}
                rename_dict.update(col_to_currency)
                self.rates_df = self.rates_df.rename(columns=rename_dict)
                
                # Convert date column to datetime
                self.rates_df['Date'] = pd.to_datetime(self.rates_df['Date'])
                
                # Clean up temporary file
                os.remove(temp_file)
                
                return True, ""
        
        except Exception as e:
            return False, f"Error fetching exchange rates: {str(e)}"
    
    def get_rate(self, date: datetime, currency: str) -> Tuple[bool, str, float]:
        """
        Get exchange rate for a specific date and currency.
        
        Args:
            date: Date for exchange rate
            currency: Currency code (e.g., USD, EUR)
        
        Returns:
            Tuple of (success, error_message, rate)
        """
        if self.rates_df is None:
            return False, "Exchange rates not fetched", 0.0
        
        if currency == 'AUD':
            return True, "", 1.0
        
        if currency not in self.rates_df.columns:
            return False, f"Currency {currency} not found in exchange rates", 0.0
        
        # Find the closest date on or before the requested date
        date_str = date.strftime('%Y-%m-%d')
        closest_date = self.rates_df[self.rates_df['Date'] <= date_str]['Date'].max()
        
        if pd.isna(closest_date):
            return False, f"No exchange rate found for {currency} on or before {date_str}", 0.0
        
        rate = self.rates_df.loc[self.rates_df['Date'] == closest_date, currency].values[0]
        
        if pd.isna(rate):
            return False, f"Exchange rate for {currency} on {closest_date} is not available", 0.0
        
        return True, "", rate
    
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
            amount_aud = amount * rate
        else:
            amount_aud = amount
        
        # Convert from AUD to target currency
        if to_currency != 'AUD':
            success, error_msg, rate = self.get_rate(date, to_currency)
            if not success:
                return False, error_msg, 0.0
            
            # FIXED: Corrected currency conversion direction
            # RBA rates are expressed as AUD per foreign currency
            # To convert AUD to foreign currency, divide by the rate
            converted_amount = amount_aud / rate
        else:
            converted_amount = amount_aud
        
        return True, "", converted_amount
