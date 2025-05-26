"""
RBA exchange rate fetching and processing utilities.
"""
import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import io
from typing import Dict, Any, Optional, List, Tuple


class RBAExchangeRates:
    """
    Class for fetching and processing exchange rates from the Reserve Bank of Australia.
    """
    
    # RBA historical data URL
    RBA_URL = "https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv"
    # Local sample file path
    SAMPLE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                   "sample_data", "f11.1-data.csv")
    
    # Mapping from currency codes to RBA series IDs
    CURRENCY_TO_SERIES_MAP = {
        'USD': 'FXRUSD',
        'EUR': 'FXREUR',
        'JPY': 'FXRJY',
        'GBP': 'FXRUKPS',
        'CNY': 'FXRCR',
        'KRW': 'FXRSKW',
        'SGD': 'FXRSD',
        'INR': 'FXRIRE',
        'THB': 'FXRTB',
        'NZD': 'FXRNZD',
        'TWD': 'FXRNTD',
        'MYR': 'FXRMR',
        'IDR': 'FXRIR',
        'VND': 'FXRVD',
        'AED': 'FXRUAED',
        'PGK': 'FXRPNGK',
        'HKD': 'FXRHKD',
        'CAD': 'FXRCD',
        'ZAR': 'FXRSARD',
        'CHF': 'FXRSF',
        'PHP': 'FXRPHP',
        'SDR': 'FXRSDR'
    }
    
    def __init__(self, use_local_file=True):
        self.rates_data = None
        self.last_updated = None
        self.use_local_file = use_local_file
        self.currency_map = {}  # Maps column names to currency codes
    
    def fetch_rates(self) -> Tuple[bool, str]:
        """
        Fetch exchange rates from RBA website or local sample file.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if self.use_local_file and os.path.exists(self.SAMPLE_FILE_PATH):
                # Read the first few rows to extract currency codes from headers
                header_df = pd.read_csv(self.SAMPLE_FILE_PATH, nrows=10)
                
                # Extract currency codes from the 'Title' row (row index 1)
                if 'Title' in header_df.columns:
                    # Create currency mapping
                    self._create_currency_map(header_df)
                
                # Use local sample file for data
                df = pd.read_csv(self.SAMPLE_FILE_PATH, skiprows=10)
                self.rates_data = self._process_rba_data(df)
                self.last_updated = datetime.now()
                return True, ""
            else:
                # Fetch from RBA website
                response = requests.get(self.RBA_URL)
                if response.status_code != 200:
                    return False, f"Failed to fetch RBA data: HTTP {response.status_code}"
                
                # Parse CSV data
                csv_data = io.StringIO(response.text)
                
                # Read header rows to extract currency codes
                header_df = pd.read_csv(csv_data, nrows=10)
                csv_data.seek(0)  # Reset file pointer
                
                # Extract currency codes from the 'Title' row
                if 'Title' in header_df.columns:
                    # Create currency mapping
                    self._create_currency_map(header_df)
                
                # Read data rows
                df = pd.read_csv(csv_data, skiprows=10)
                
                # Process the dataframe to extract exchange rates
                self.rates_data = self._process_rba_data(df)
                self.last_updated = datetime.now()
                
                return True, ""
        except Exception as e:
            return False, f"Error fetching RBA exchange rates: {str(e)}"
    
    def _create_currency_map(self, header_df: pd.DataFrame) -> None:
        """
        Create mapping from column names to currency codes based on header rows.
        
        Args:
            header_df: DataFrame containing header rows
        """
        try:
            # Get the 'Title' row which contains currency codes
            title_row = header_df.iloc[1]  # Second row (index 1)
            
            # Create mapping from column positions to currency codes
            self.currency_map = {}
            
            for i, value in enumerate(title_row):
                if pd.notna(value) and isinstance(value, str):
                    # Extract currency code from format like 'A$1=USD'
                    if '=' in value:
                        currency_code = value.split('=')[1]
                        # Map the column name (which will be 'Unnamed: i' in the data) to the currency code
                        col_name = f"Unnamed: {i}" if i > 0 else header_df.columns[0]
                        self.currency_map[col_name] = currency_code
        except Exception as e:
            print(f"Error creating currency map: {str(e)}")
    
    def _process_rba_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the raw RBA data into a usable format.
        
        Args:
            df: Raw dataframe from RBA CSV
            
        Returns:
            Processed dataframe with date index and currency columns
        """
        try:
            # The first column is the date but has no header
            # Rename the first column to 'Date'
            data_rows = df.copy()
            data_rows.rename(columns={data_rows.columns[0]: 'Date'}, inplace=True)
            
            # Convert the 'Date' column to datetime
            data_rows['Date'] = pd.to_datetime(data_rows['Date'], format='%d-%b-%Y', errors='coerce')
            
            # Drop rows with invalid dates
            data_rows = data_rows.dropna(subset=['Date'])
            
            # Set the 'Date' column as the index
            data_rows.set_index('Date', inplace=True)
            
            # Convert all rate columns to numeric values
            for col in data_rows.columns:
                data_rows[col] = pd.to_numeric(data_rows[col], errors='coerce')
            
            # Rename columns based on currency map
            if self.currency_map:
                rename_dict = {col: self.currency_map.get(col, col) for col in data_rows.columns if col in self.currency_map}
                data_rows.rename(columns=rename_dict, inplace=True)
            
            # Sort by date (newest first)
            data_rows = data_rows.sort_index(ascending=False)
            
            return data_rows
            
        except Exception as e:
            # If processing fails, return an empty dataframe with date index
            print(f"Error processing RBA data: {str(e)}")
            return pd.DataFrame(index=pd.DatetimeIndex([]))
    
    def get_rate(self, date: datetime, currency: str) -> Tuple[bool, str, Optional[float]]:
        """
        Get exchange rate for a specific date and currency.
        If rate is not available for the exact date, use the most recent past date.
        
        Args:
            date: Date for which to get the exchange rate
            currency: Currency code (e.g., 'USD')
            
        Returns:
            Tuple of (success, error_message, rate)
        """
        if self.rates_data is None or self.rates_data.empty:
            success, error_msg = self.fetch_rates()
            if not success:
                return False, error_msg, None
        
        try:
            # Convert currency code to RBA series ID
            series_id = self.CURRENCY_TO_SERIES_MAP.get(currency)
            if not series_id:
                return False, f"Unsupported currency code: {currency}", None
            
            # Format the date to match the index format
            date_str = date.strftime('%Y-%m-%d')
            
            # Find the exact date or the closest previous date
            available_dates = self.rates_data.index
            
            # Try to find the exact date
            if date in available_dates:
                if series_id in self.rates_data.columns:
                    rate = self.rates_data.loc[date, series_id]
                    if pd.notna(rate):
                        return True, "", float(rate)
            
            # If exact date not found, find the most recent past date
            past_dates = [d for d in available_dates if d < date]
            if past_dates:
                most_recent = max(past_dates)
                if series_id in self.rates_data.columns:
                    rate = self.rates_data.loc[most_recent, series_id]
                    if pd.notna(rate):
                        return True, "", float(rate)
            
            return False, f"No exchange rate found for {currency} on or before {date_str}", None
            
        except Exception as e:
            return False, f"Error retrieving exchange rate: {str(e)}", None
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str, 
                      date: datetime) -> Tuple[bool, str, Optional[float]]:
        """
        Convert an amount from one currency to another using RBA rates.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date for the conversion rate
            
        Returns:
            Tuple of (success, error_message, converted_amount)
        """
        if from_currency == to_currency:
            return True, "", amount
        
        # For conversion to AUD
        if to_currency == 'AUD':
            success, error_msg, rate = self.get_rate(date, from_currency)
            if not success:
                return False, error_msg, None
            
            # RBA rates are typically AUD per foreign currency
            # The rate is how many foreign currency units per 1 AUD
            # So to convert from foreign to AUD, we divide by the rate
            converted = amount / rate
            return True, "", converted
        
        # For conversion from AUD
        elif from_currency == 'AUD':
            success, error_msg, rate = self.get_rate(date, to_currency)
            if not success:
                return False, error_msg, None
            
            # RBA rates are typically AUD per foreign currency
            # The rate is how many foreign currency units per 1 AUD
            # So to convert from AUD to foreign, we multiply by the rate
            converted = amount * rate
            return True, "", converted
        
        # For conversion between two non-AUD currencies
        else:
            # Convert to AUD first, then to target currency
            success1, error_msg1, rate1 = self.get_rate(date, from_currency)
            if not success1:
                return False, error_msg1, None
            
            success2, error_msg2, rate2 = self.get_rate(date, to_currency)
            if not success2:
                return False, error_msg2, None
            
            # Convert through AUD
            aud_amount = amount / rate1  # Convert from source to AUD
            converted = aud_amount * rate2  # Convert from AUD to target
            
            return True, "", converted
