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
    # Check if transaction file was uploaded
    if 'transactions' not in request.files:
        return jsonify({'success': False, 'error': 'Transaction file is required'}), 400
    
    transactions_file = request.files['transactions']
    
    # Check if transaction filename is empty
    if transactions_file.filename == '':
        return jsonify({'success': False, 'error': 'Transaction file is required'}), 400
    
    try:
        # Save transaction file to temporary location
        transactions_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                        f"{uuid.uuid4()}_{transactions_file.filename}")
        transactions_file.save(transactions_path)
        
        # Process transactions file
        success_tx, error_tx, transactions_df = process_trade_transactions(transactions_path)
        if not success_tx:
            # Clean up file
            os.remove(transactions_path)
            return jsonify({'success': False, 'error': f'Transactions file error: {error_tx}'}), 400
        
        # Initialize tax calculator
        calculator = TaxCalculator()
        
        # Check if opening balance file was uploaded (now optional)
        opening_balance_df = None
        opening_balance_path = None
        
        if 'opening_balance' in request.files and request.files['opening_balance'].filename != '':
            opening_balance_file = request.files['opening_balance']
            opening_balance_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                              f"{uuid.uuid4()}_{opening_balance_file.filename}")
            opening_balance_file.save(opening_balance_path)
            
            # Process opening balance file
            success_ob, error_ob, opening_balance_df = process_opening_balance(opening_balance_path)
            if not success_ob:
                # Clean up files
                os.remove(transactions_path)
                if opening_balance_path:
                    os.remove(opening_balance_path)
                return jsonify({'success': False, 'error': f'Opening balance file error: {error_ob}'}), 400
            
            calculator.set_opening_balance(opening_balance_df)
        
        # Set transactions
        calculator.set_transactions(transactions_df)
        
        # Calculate tax
        success_calc, error_calc, results = calculator.calculate_tax()
        if not success_calc:
            # Clean up files
            os.remove(transactions_path)
            if opening_balance_path:
                os.remove(opening_balance_path)
            return jsonify({'success': False, 'error': f'Calculation error: {error_calc}'}), 400
        
        # Clean up files
        os.remove(transactions_path)
        if opening_balance_path:
            os.remove(opening_balance_path)
        
        # Render the results template and return it directly
        rendered_html = render_template('results.html', results=results)
        return jsonify({'success': True, 'html': rendered_html, 'results': results})
        
    except Exception as e:
        # Clean up files if they exist
        if 'transactions_path' in locals() and os.path.exists(transactions_path):
            os.remove(transactions_path)
        if 'opening_balance_path' in locals() and opening_balance_path and os.path.exists(opening_balance_path):
            os.remove(opening_balance_path)
        
        return jsonify({'success': False, 'error': f'Error processing files: {str(e)}'}), 500


@app.route('/results', methods=['GET', 'POST'])
def results():
    """Display tax calculation results."""
    if request.method == 'POST' and request.is_json:
        # Get data directly from the AJAX request
        data = request.get_json()
        if 'results' in data:
            # Render the results template with the provided data
            rendered_html = render_template('results.html', results=data['results'])
            return jsonify({'success': True, 'html': rendered_html})
        else:
            return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    else:
        # Direct access without data should show error
        return render_template('error.html', error='No calculation results found. Please upload files first.')


@app.route('/details/<element>', methods=['GET', 'POST'])
def details(element):
    """Display detailed breakdown of a specific element."""
    if request.method == 'POST' and request.is_json:
        # Get data directly from the AJAX request
        data = request.get_json()
        if 'element_data' in data and 'element_name' in data:
            # Render the details template with the provided data
            # Also pass the full results data for the "Back to Results" functionality
            rendered_html = render_template('details.html', 
                                           element_data=data['element_data'], 
                                           element_name=data['element_name'],
                                           full_results=data.get('full_results', {}))
            return jsonify({'success': True, 'html': rendered_html})
        else:
            return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    else:
        # Direct access without data should show error
        return render_template('error.html', error='Please calculate tax liability first and access details from the results page.')


@app.route('/clear')
def clear_session():
    """Redirect to home page."""
    return redirect('/')


if __name__ == '__main__':
    # Fetch RBA rates on startup
    rba_rates.fetch_rates()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
