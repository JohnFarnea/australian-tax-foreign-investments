"""
Test script for validating the RBA exchange rate loading functionality.
"""
import sys
import os
import pandas as pd
from datetime import datetime
import importlib

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force reload of the module to ensure latest code is used
if 'app.src.utils.rba_rates' in sys.modules:
    del sys.modules['app.src.utils.rba_rates']

# Import the RBAExchangeRates class
from app.src.utils.rba_rates import RBAExchangeRates

def test_rba_rates():
    """Test the RBA exchange rate loading and retrieval."""
    print("Testing RBA Exchange Rates with Row 11 Header Parser...")
    
    # Initialize RBA rates
    rba_rates = RBAExchangeRates()
    
    # Fetch rates
    success, error_msg = rba_rates.fetch_rates()
    print(f"Fetch rates success: {success}")
    if not success:
        print(f"Error: {error_msg}")
        return
    
    # Check if rates_data is loaded
    if not hasattr(rba_rates, 'rates_data') or rba_rates.rates_data is None:
        print("Error: rates_data is None or not found")
        return
    
    # Print dataframe info
    print("\nDataFrame Info:")
    print(f"Shape: {rba_rates.rates_data.shape}")
    print(f"Columns: {rba_rates.rates_data.columns.tolist()}")
    
    # Check if Date column exists
    if 'Date' in rba_rates.rates_data.columns:
        print(f"Date range: {rba_rates.rates_data['Date'].min()} to {rba_rates.rates_data['Date'].max()}")
        print("\nFirst 5 rows of DataFrame:")
        print(rba_rates.rates_data.head())
    else:
        print("Warning: 'Date' column not found in DataFrame")
        print("Available columns:", rba_rates.rates_data.columns.tolist())
        return
    
    # Test getting rates for different currencies
    test_date = datetime(2024, 1, 15)
    # Update to use the actual currency codes from the file
    currencies = ['USD', 'EUR', 'JY', 'UKPS']
    
    print("\nTesting rate retrieval for date:", test_date.strftime('%Y-%m-%d'))
    for currency in currencies:
        success, error_msg, rate = rba_rates.get_rate(test_date, currency)
        print(f"{currency}: success={success}, rate={rate if success else 'N/A'}, error={error_msg if not success else 'None'}")
    
    # Test currency conversion
    print("\nTesting currency conversion:")
    amount = 1000.0
    from_currency = 'USD'
    to_currency = 'AUD'
    success, error_msg, converted = rba_rates.convert_amount(amount, from_currency, to_currency, test_date)
    print(f"Convert {amount} {from_currency} to {to_currency}: {converted if success else 'N/A'} (success={success})")
    
    # Test reverse conversion
    from_currency = 'AUD'
    to_currency = 'USD'
    success, error_msg, converted = rba_rates.convert_amount(amount, from_currency, to_currency, test_date)
    print(f"Convert {amount} {from_currency} to {to_currency}: {converted if success else 'N/A'} (success={success})")

if __name__ == "__main__":
    test_rba_rates()
