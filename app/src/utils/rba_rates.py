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
    
    def __init__(self):
        """
        Initialize RBA exchange rates.
        """
        self.rates_data = None
        self.rba_url = "https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv"
        # Corrected path to match actual file location
        self.local_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "../sample_data", "f11.1-data.csv")
        self.last_updated = None
    
    def fetch_rates(self) -> Tuple[bool, str]:
        """
        Fetch exchange rates from local file.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Check if local file exists
            if not os.path.exists(self.local_file):
                return False, f"Local file not found: {self.local_file}"
            
            # Read the CSV file, skipping to row 11 which contains the header
            df = pd.read_csv(self.local_file, skiprows=10)
            
            # Process the dataframe to clean up column names and format data
            df = self._process_rba_data(df)
            
            self.rates_data = df
            self.last_updated = datetime.now()
            
            return True, ""
        
        except Exception as e:
            return False, f"Error fetching exchange rates: {str(e)}"
    
    def _process_rba_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the raw RBA data into a usable format.
        
        Args:
            df: Raw dataframe from RBA CSV
            
        Returns:
            Processed dataframe with date index and currency columns
        """
        try:
            # Rename 'Series ID' column to 'Date'
            if 'Series ID' in df.columns:
                df = df.rename(columns={'Series ID': 'Date'})
            
            # Remove 'FXR' prefix from currency columns
            new_columns = {}
            for col in df.columns:
                if col.startswith('FXR') and col != 'FXR':
                    new_columns[col] = col[3:]  # Remove 'FXR' prefix
            
            # Apply column renaming
            df = df.rename(columns=new_columns)
            
            # Convert date column to datetime
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Drop rows with invalid dates
            df = df.dropna(subset=['Date'])
            
            # Select only relevant columns (Date and currency columns)
            # Ignore empty columns after FXRSDR
            relevant_cols = ['Date']
            for col in df.columns:
                if col != 'Date' and not col.startswith('Unnamed'):
                    relevant_cols.append(col)
            
            df = df[relevant_cols]
            
            # Check for valid rates (not zero or NaN)
            for col in df.columns:
                if col != 'Date':
                    # Replace zeros with NaN
                    df[col] = df[col].replace(0, pd.NA)
            
            # Drop rows where all currency rates are NaN
            df = df.dropna(how='all', subset=[col for col in df.columns if col != 'Date'])
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error processing RBA data: {str(e)}")
    
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
            # Convert date to pandas Timestamp for comparison
            pd_date = pd.Timestamp(date)
            
            # Find dates on or before the requested date
            valid_dates = self.rates_data[self.rates_data['Date'] <= pd_date]
            
            if valid_dates.empty:
                return False, f"No exchange rate data available on or before {date_str}", 0.0
            
            # Get the most recent date
            closest_date_row = valid_dates.iloc[-1]
            rate = closest_date_row[currency]
            
            # Validate the rate
            if pd.isna(rate) or rate == 0:
                return False, f"Invalid exchange rate (0 or NaN) for {currency} on {closest_date_row['Date'].strftime('%Y-%m-%d')}", 0.0
            
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
