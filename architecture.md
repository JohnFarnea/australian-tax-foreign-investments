# Australian Tax Foreign Investments Web Application - Architecture Design

## Overview
This document outlines the architecture for the Australian Tax Foreign Investments web application. The application allows Australian companies to calculate tax liabilities when trading foreign shares, following specific rules for traders.

## Application Components

### 1. Core Modules

#### 1.1 File Processing Module
- **Purpose**: Handle file uploads (CSV and Excel) and extract data
- **Components**:
  - File validation (format, required columns)
  - Data extraction for opening balance files
  - Data extraction for trade transaction files
  - Data normalization and preparation for calculations

#### 1.2 RBA Exchange Rate Module
- **Purpose**: Fetch and process exchange rates from RBA
- **Components**:
  - API integration with RBA website
  - Rate caching mechanism
  - Fallback logic for missing dates (use most recent past date)
  - Currency conversion utilities

#### 1.3 Tax Calculation Module
- **Purpose**: Implement tax calculation logic
- **Components**:
  - Opening balance processing
  - Cost of shares sold calculation
  - Currency conversion for transactions
  - Gross trading income calculation
  - Detailed transaction tracking for drill-down views

#### 1.4 Reporting Module
- **Purpose**: Generate reports and interactive views
- **Components**:
  - Gross Trading Income statement generation
  - Detailed transaction view generation
  - Data formatting for UI presentation

### 2. Web Interface

#### 2.1 Routes and Endpoints
- **Home Page** (`/`): Main interface with file upload forms
- **Process** (`/process`): Handle file uploads and initiate calculations
- **Results** (`/results`): Display Gross Trading Income statement
- **Details** (`/details/<element_id>`): Drill-down view for specific elements

#### 2.2 UI Components
- File upload forms with validation
- Processing status indicators
- Interactive results display
- Drill-down navigation
- Error messaging

## Data Flow

1. **User Input**:
   - User uploads opening balance file
   - User uploads trade transactions file

2. **Processing**:
   - Files are validated and parsed
   - RBA exchange rates are fetched for relevant dates
   - Tax calculations are performed
   - Results are prepared for display

3. **Output**:
   - Gross Trading Income statement is displayed
   - User can interact with results to view detailed breakdowns

## Technical Specifications

### Flask Application Structure
```
app/
├── venv/
├── src/
│   ├── models/
│   │   └── calculation.py  # Tax calculation models
│   ├── routes/
│   │   ├── main_routes.py  # Main application routes
│   │   └── api_routes.py   # API endpoints for AJAX requests
│   ├── static/
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript for interactive UI
│   │   └── img/           # Images and icons
│   ├── templates/         # Jinja2 templates
│   │   ├── index.html     # Home page
│   │   ├── results.html   # Results display
│   │   └── details.html   # Drill-down view
│   ├── utils/
│   │   ├── file_processor.py  # File upload and processing
│   │   ├── rba_rates.py       # RBA exchange rate fetching
│   │   └── tax_calculator.py  # Tax calculation logic
│   └── main.py            # Application entry point
└── requirements.txt       # Dependencies
```

### Dependencies
- Flask: Web framework
- Pandas: Data processing and analysis
- Openpyxl: Excel file handling
- Requests: HTTP requests for RBA data
- Bootstrap: Frontend styling
- Chart.js: Interactive data visualization
- jQuery: DOM manipulation and AJAX requests

### Security Considerations
- No data persistence (as per requirements)
- Input validation for all file uploads
- Error handling for invalid inputs
- Rate limiting for RBA API requests

## Implementation Plan

1. **Setup Project Structure**:
   - Create directory structure
   - Initialize Flask application
   - Set up static and template directories

2. **Implement Core Functionality**:
   - Develop file processing utilities
   - Implement RBA exchange rate fetching
   - Create tax calculation logic

3. **Build Web Interface**:
   - Design and implement templates
   - Create interactive components
   - Implement routing logic

4. **Testing and Validation**:
   - Test with sample data
   - Validate calculations
   - Ensure responsive UI

5. **Deployment**:
   - Prepare for deployment
   - Deploy application
   - Verify functionality
