"""
File processing utilities for handling CSV and Excel files.
"""
import pandas as pd
from typing import Tuple, Any


def process_opening_balance(file_path: str) -> Tuple[bool, str, Any]:
    """
    Process opening balance file (CSV or Excel).
    
    Args:
        file_path: Path to the opening balance file
    
    Returns:
        Tuple of (success, error_message, dataframe)
    """
    try:
        # Determine file type based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            return False, "Unsupported file format. Please use CSV or Excel.", None
        
        # Validate required columns
        required_columns = ['Symbol', 'Quantity', 'Total Cost in AUD']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}", None
        
        # Validate data types
        try:
            df['Quantity'] = pd.to_numeric(df['Quantity'])
            df['Total Cost in AUD'] = pd.to_numeric(df['Total Cost in AUD'])
        except Exception as e:
            return False, f"Error converting numeric columns: {str(e)}", None
        
        # Validate data values
        if (df['Quantity'] <= 0).any():
            return False, "Quantity must be positive for opening balance.", None
        
        return True, "", df
        
    except Exception as e:
        return False, f"Error processing opening balance file: {str(e)}", None


def process_trade_transactions(file_path: str) -> Tuple[bool, str, Any]:
    """
    Process trade transactions file (CSV or Excel).
    
    Args:
        file_path: Path to the trade transactions file
    
    Returns:
        Tuple of (success, error_message, dataframe)
    """
    try:
        # Determine file type based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            return False, "Unsupported file format. Please use CSV or Excel.", None
        
        # Validate required columns
        required_columns = ['Date', 'Symbol', 'Quantity', 'Unit Price', 'Commission', 'Currency']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}", None
        
        # Convert date column to datetime
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except Exception as e:
            return False, f"Error converting date column: {str(e)}", None
        
        # Validate data types
        try:
            df['Quantity'] = pd.to_numeric(df['Quantity'])
            df['Unit Price'] = pd.to_numeric(df['Unit Price'])
            df['Commission'] = pd.to_numeric(df['Commission'])
        except Exception as e:
            return False, f"Error converting numeric columns: {str(e)}", None
        
        # Calculate derived columns
        df['Total Gross Value'] = df['Quantity'] * df['Unit Price']
        df['Net Value'] = df['Total Gross Value'] - df['Commission']
        
        return True, "", df
        
    except Exception as e:
        return False, f"Error processing trade transactions file: {str(e)}", None
