"""
RBA exchange rate fetching and processing utilities.
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
from typing import Dict, Any, Optional, List, Tuple


class RBAExchangeRates:
    """
    Class for fetching and processing exchange rates from the Reserve Bank of Australia.
    """
    
    # RBA historical data URL
    RBA_URL = "https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv"
    
    def __init__(self):
        self.rates_data = None
        self.last_updated = None
    
    def fetch_rates(self) -> Tuple[bool, str]:
        """
        Fetch exchange rates from RBA website.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            response = requests.get(self.RBA_URL)
            if response.status_code != 200:
                return False, f"Failed to fetch RBA data: HTTP {response.status_code}"
            
            # Parse CSV data
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data, skiprows=0)
            
            # Process the dataframe to extract exchange rates
            # The RBA CSV format may need specific handling
            self.rates_data = self._process_rba_data(df)
            self.last_updated = datetime.now()
            
            return True, ""
        except Exception as e:
            return False, f"Error fetching RBA exchange rates: {str(e)}"
    
    def _process_rba_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the raw RBA data into a usable format.
        
        Args:
            df: Raw dataframe from RBA CSV
            
        Returns:
            Processed dataframe with date index and currency columns
        """
        # Note: This is a placeholder implementation
        # The actual implementation will depend on the exact format of the RBA CSV
        
        # Typically, we would:
        # 1. Convert the 'Date' column to datetime
        # 2. Set the 'Date' column as the index
        # 3. Clean up column names to match currency codes
        # 4. Handle any missing values
        
        # For now, we'll return the original dataframe
        # This will need to be updated based on actual RBA data format
        return df
    
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
        if self.rates_data is None:
            success, error_msg = self.fetch_rates()
            if not success:
                return False, error_msg, None
        
        try:
            # Convert date to string format used in the dataframe
            date_str = date.strftime('%Y-%m-%d')
            
            # Check if the exact date exists
            if date_str in self.rates_data.index:
                if currency in self.rates_data.columns:
                    rate = self.rates_data.loc[date_str, currency]
                    if pd.notna(rate):
                        return True, "", float(rate)
            
            # If exact date not found or rate is NaN, find the most recent past date
            past_dates = [d for d in self.rates_data.index if d < date_str]
            if past_dates:
                most_recent = max(past_dates)
                if currency in self.rates_data.columns:
                    rate = self.rates_data.loc[most_recent, currency]
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
            converted = amount * rate
            return True, "", converted
        
        # For conversion from AUD
        elif from_currency == 'AUD':
            success, error_msg, rate = self.get_rate(date, to_currency)
            if not success:
                return False, error_msg, None
            
            # RBA rates are typically AUD per foreign currency
            converted = amount / rate
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
            aud_amount = amount * rate1
            converted = aud_amount / rate2
            
            return True, "", converted
