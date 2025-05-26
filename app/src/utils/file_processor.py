"""
File processing utilities for handling CSV and Excel uploads.
"""
import pandas as pd
import os
from typing import Dict, Any, Tuple, List, Optional


def validate_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate if the uploaded file is a valid CSV or Excel file.
    
    Args:
        file_path: Path to the uploaded file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext not in ['.csv', '.xlsx', '.xls']:
        return False, "File must be CSV or Excel format"
    
    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Check if dataframe is empty
        if df.empty:
            return False, "File is empty"
            
        return True, ""
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def process_opening_balance(file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Process opening balance file (CSV or Excel).
    
    Expected columns: Symbol, Quantity, Total Cost in AUD
    
    Args:
        file_path: Path to the opening balance file
        
    Returns:
        Tuple of (success, error_message, dataframe)
    """
    is_valid, error_msg = validate_file(file_path)
    if not is_valid:
        return False, error_msg, None
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Check required columns
        required_cols = ['Symbol', 'Quantity', 'Total Cost in AUD']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}", None
        
        # Validate data types
        try:
            df['Quantity'] = pd.to_numeric(df['Quantity'])
            df['Total Cost in AUD'] = pd.to_numeric(df['Total Cost in AUD'])
        except Exception as e:
            return False, f"Invalid numeric data in Quantity or Total Cost columns: {str(e)}", None
        
        # Ensure all quantities are positive for opening balance
        if (df['Quantity'] <= 0).any():
            return False, "Opening balance quantities must be positive", None
            
        return True, "", df
    
    except Exception as e:
        return False, f"Error processing opening balance file: {str(e)}", None


def process_trade_transactions(file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Process trade transactions file (CSV or Excel).
    
    Expected columns: Date, Symbol, Quantity, Unit Price, Total Gross Value, 
                     Commission, Net Value, Currency
    
    Args:
        file_path: Path to the trade transactions file
        
    Returns:
        Tuple of (success, error_message, dataframe)
    """
    is_valid, error_msg = validate_file(file_path)
    if not is_valid:
        return False, error_msg, None
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Check required columns
        required_cols = [
            'Date', 'Symbol', 'Quantity', 'Unit Price', 
            'Total Gross Value', 'Commission', 'Net Value', 'Currency'
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}", None
        
        # Validate data types
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            df['Quantity'] = pd.to_numeric(df['Quantity'])
            df['Unit Price'] = pd.to_numeric(df['Unit Price'])
            df['Total Gross Value'] = pd.to_numeric(df['Total Gross Value'])
            df['Commission'] = pd.to_numeric(df['Commission'])
            df['Net Value'] = pd.to_numeric(df['Net Value'])
        except Exception as e:
            return False, f"Invalid data in one or more columns: {str(e)}", None
        
        # Validate buy/sell logic (positive for buy, negative for sell)
        if not ((df['Quantity'] > 0) & (df['Total Gross Value'] > 0) | 
                (df['Quantity'] < 0) & (df['Total Gross Value'] < 0)).all():
            return False, "Quantity and Total Gross Value signs must match (both positive for buy, both negative for sell)", None
            
        return True, "", df
    
    except Exception as e:
        return False, f"Error processing trade transactions file: {str(e)}", None
