# Test Plan for Australian Tax Foreign Investments Web Application

## Overview
This document outlines the test plan for validating the Australian Tax Foreign Investments web application. The application allows Australian companies to calculate tax liabilities when trading foreign shares, following specific rules for traders.

## Test Environment
- Local development environment
- Flask development server
- Sample test files:
  - `opening_balance.csv`: Contains opening balance data
  - `trade_transactions.csv`: Contains trade transaction data

## Test Cases

### 1. File Upload Functionality

#### 1.1 Opening Balance File Upload
- **Test ID**: FU-OB-001
- **Description**: Upload a valid opening balance CSV file
- **Test Steps**:
  1. Navigate to the home page
  2. Select the sample opening balance CSV file
  3. Submit the form
- **Expected Result**: File is successfully uploaded and validated

#### 1.2 Trade Transactions File Upload
- **Test ID**: FU-TT-001
- **Description**: Upload a valid trade transactions CSV file
- **Test Steps**:
  1. Navigate to the home page
  2. Select the sample trade transactions CSV file
  3. Submit the form
- **Expected Result**: File is successfully uploaded and validated

#### 1.3 Invalid File Format Handling
- **Test ID**: FU-ERR-001
- **Description**: Attempt to upload files with invalid formats
- **Test Steps**:
  1. Navigate to the home page
  2. Select files with invalid formats or missing required columns
  3. Submit the form
- **Expected Result**: Application displays appropriate error messages

### 2. RBA Exchange Rate Integration

#### 2.1 Exchange Rate Fetching
- **Test ID**: RBA-001
- **Description**: Verify that the application fetches exchange rates from RBA
- **Test Steps**:
  1. Upload valid opening balance and trade transactions files
  2. Observe the application logs and behavior
- **Expected Result**: Exchange rates are successfully fetched and used in calculations

#### 2.2 Fallback for Missing Dates
- **Test ID**: RBA-002
- **Description**: Verify fallback logic for dates without exchange rates
- **Test Steps**:
  1. Include transactions on weekends/holidays in the test data
  2. Upload and process the files
- **Expected Result**: Application uses the most recent past date's exchange rate

### 3. Tax Calculation Logic

#### 3.1 Cost of Shares Sold Calculation
- **Test ID**: CALC-001
- **Description**: Verify correct calculation of cost of shares sold
- **Test Steps**:
  1. Upload valid opening balance and trade transactions files
  2. Process the calculation
  3. Review the results
- **Expected Result**: Cost of shares sold = Opening Balance + Purchases - Closing Balance

#### 3.2 Gross Trading Income Calculation
- **Test ID**: CALC-002
- **Description**: Verify correct calculation of gross trading income
- **Test Steps**:
  1. Upload valid opening balance and trade transactions files
  2. Process the calculation
  3. Review the results
- **Expected Result**: Gross Trading Income = Sales - Cost of Shares Sold

#### 3.3 Currency Conversion
- **Test ID**: CALC-003
- **Description**: Verify correct currency conversion for transactions
- **Test Steps**:
  1. Upload files with transactions in foreign currencies
  2. Process the calculation
  3. Review the detailed results
- **Expected Result**: Foreign currency values are correctly converted to AUD

### 4. Interactive UI

#### 4.1 Results Display
- **Test ID**: UI-001
- **Description**: Verify that results are displayed correctly
- **Test Steps**:
  1. Complete a calculation
  2. Review the results page
- **Expected Result**: Results are displayed in a clear, organized manner

#### 4.2 Drill-Down Functionality
- **Test ID**: UI-002
- **Description**: Verify drill-down functionality for detailed views
- **Test Steps**:
  1. Complete a calculation
  2. Click on various elements to view detailed breakdowns
- **Expected Result**: Detailed views are displayed correctly for each element

#### 4.3 Responsive Design
- **Test ID**: UI-003
- **Description**: Verify responsive design for different screen sizes
- **Test Steps**:
  1. Access the application on different devices or using responsive design tools
  2. Navigate through the application
- **Expected Result**: UI adapts appropriately to different screen sizes

## Test Results and Issues

### Completed Tests
- [List of completed tests with pass/fail status]

### Issues Found
- [List of issues found during testing]

### Recommendations
- [Recommendations for addressing issues and improving the application]

## Conclusion
[Summary of test results and overall assessment of the application's readiness]
