from flask import Flask, render_template, request, jsonify, session
import os
import sys
import pandas as pd
import tempfile
import uuid

# Import custom modules
from src.utils.file_processor import process_opening_balance, process_trade_transactions
from src.utils.rba_rates import RBAExchangeRates
from src.models.calculation import TaxCalculator

# Required configuration for deployment
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # Use temp directory for uploads

# Initialize RBA exchange rates
rba_rates = RBAExchangeRates()


@app.route('/')
def index():
    """Render the main page with file upload forms."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads for opening balance and transactions."""
    # Check if files were uploaded
    if 'opening_balance' not in request.files or 'transactions' not in request.files:
        return jsonify({'success': False, 'error': 'Both files are required'}), 400
    
    opening_balance_file = request.files['opening_balance']
    transactions_file = request.files['transactions']
    
    # Check if filenames are empty
    if opening_balance_file.filename == '' or transactions_file.filename == '':
        return jsonify({'success': False, 'error': 'Both files are required'}), 400
    
    try:
        # Save files to temporary location
        opening_balance_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                           f"{uuid.uuid4()}_{opening_balance_file.filename}")
        transactions_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                        f"{uuid.uuid4()}_{transactions_file.filename}")
        
        opening_balance_file.save(opening_balance_path)
        transactions_file.save(transactions_path)
        
        # Process opening balance file
        success_ob, error_ob, opening_balance_df = process_opening_balance(opening_balance_path)
        if not success_ob:
            # Clean up files
            os.remove(opening_balance_path)
            os.remove(transactions_path)
            return jsonify({'success': False, 'error': f'Opening balance file error: {error_ob}'}), 400
        
        # Process transactions file
        success_tx, error_tx, transactions_df = process_trade_transactions(transactions_path)
        if not success_tx:
            # Clean up files
            os.remove(opening_balance_path)
            os.remove(transactions_path)
            return jsonify({'success': False, 'error': f'Transactions file error: {error_tx}'}), 400
        
        # Initialize tax calculator
        calculator = TaxCalculator()
        calculator.set_opening_balance(opening_balance_df)
        calculator.set_transactions(transactions_df)
        
        # Calculate tax
        success_calc, error_calc, results = calculator.calculate_tax()
        if not success_calc:
            # Clean up files
            os.remove(opening_balance_path)
            os.remove(transactions_path)
            return jsonify({'success': False, 'error': f'Calculation error: {error_calc}'}), 400
        
        # Store results in session
        session['tax_results'] = results
        
        # Clean up files
        os.remove(opening_balance_path)
        os.remove(transactions_path)
        
        return jsonify({'success': True, 'redirect': '/results'})
        
    except Exception as e:
        # Clean up files if they exist
        if 'opening_balance_path' in locals() and os.path.exists(opening_balance_path):
            os.remove(opening_balance_path)
        if 'transactions_path' in locals() and os.path.exists(transactions_path):
            os.remove(transactions_path)
        
        return jsonify({'success': False, 'error': f'Error processing files: {str(e)}'}), 500


@app.route('/results')
def results():
    """Display tax calculation results."""
    # Check if results exist in session
    if 'tax_results' not in session:
        return render_template('error.html', error='No calculation results found. Please upload files first.')
    
    results = session['tax_results']
    return render_template('results.html', results=results)


@app.route('/details/<element>')
def details(element):
    """Display detailed breakdown of a specific element."""
    # Check if results exist in session
    if 'tax_results' not in session:
        return render_template('error.html', error='No calculation results found. Please upload files first.')
    
    results = session['tax_results']
    
    # Check if the requested element exists in results
    if element not in results:
        return render_template('error.html', error=f'Element {element} not found in results.')
    
    element_data = results[element]
    element_name = element.replace('_', ' ').title()
    
    return render_template('details.html', element_name=element_name, element_data=element_data)


@app.route('/clear')
def clear_session():
    """Clear session data."""
    session.clear()
    return jsonify({'success': True})


if __name__ == '__main__':
    # Fetch RBA rates on startup
    rba_rates.fetch_rates()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
