# Australian Tax Foreign Investments

Calculation of Australian Tax Liabilities on Foreign Share Trading

A web application developed in Python that allows an Australian Company to calculate its tax liability when it trades in foreign shares.

## Overview

This application helps Australian companies classified as Traders to accurately calculate their tax liabilities from foreign share trading activities. The application handles currency conversion, tracks share purchases and sales, and generates comprehensive trading income statements in compliance with Australian tax regulations.

## Tax Calculation Rules

For a company classified as a Trader, the rules for calculation of tax are as follows:

Gross Trading Income = Sales - Cost of Shares Sold

Cost of Shares Sold = Opening Balance of Shares + Purchases - Closing Balance of Shares

Opening Balance of Shares and Closing Balance of Shares are the Values at time of Purchase - i.e., the Cost Value. This ensures only Realised Gains are reported in Gross Trading Income.

Sales Values are to be translated from the Foreign Currency to AUD at the time of the Sale Transaction. Purchases Values are to be translated from the Foreign Currency to AUD at the time of the Purchase Transaction.

## Implementation Details

### Currency Conversion

The application implements currency conversion from foreign currencies (e.g., USD) to AUD. The conversion rate is approximately $1 AUD to $0.60 USD. This conversion is applied to all transactions to ensure accurate tax calculations in the Australian currency.

### Share Sales Calculation

When calculating the cost of shares sold, the application subtracts sales at cost value from the balance list, not at the selling price. This ensures that the calculation of closing balance is accurate and that only realized gains are included in the Gross Trading Income.

### Opening Balance File

The Opening Balance file is optional. If an investor does not have any existing positions, they can proceed without uploading an Opening Balance file. The application will calculate the tax liability based solely on the transactions during the reporting period.

## Functionality of the Web Site

* Allow the User to upload a spreadsheet or CSV file containing their Opening Balance of Shares (optional). The file should include:
  * Symbol, Quantity, Total Cost in AUD

* Allow the User to upload a spreadsheet or CSV file containing the share trades for the year. The file should include:
  * Date, Symbol, Quantity (positive for Buy and negative for sell), Unit Price, Total Gross Value (+ve or -ve), Commission (normally -ve), Net Value (+ve or -ve), Currency (ie. USD)

* Obtain ATO approved currency conversion rates from the RBA Web Site Page Here - [https://www.rba.gov.au/statistics/historical-data.html#exchange-rates](https://www.rba.gov.au/statistics/historical-data.html#exchange-rates)
  * The application includes a fallback mechanism for exchange rate data in case of import errors

* Generate a Gross Trading Income statement specifying the values as listed above in AUD

* Allow the user to drill down to a detailed view of each element of the Gross Trading Income Statement which will list the transactions including the conversion to AUD

## Technical Implementation

The application is built using Python with a web interface. It processes CSV or spreadsheet files, performs currency conversions, and generates detailed tax reports. The implementation includes:

1. File upload functionality for both Opening Balance (optional) and Trade Transaction files
2. Currency conversion using RBA exchange rate data with fallback mechanisms
3. Calculation engine that properly accounts for share purchases and sales
4. Detailed reporting with drill-down capabilities

## Sample Data

The application includes sample test files for opening balance and trade transactions that can be used to test the functionality and understand the required format.

## Testing

A comprehensive test plan has been implemented to ensure the accuracy of calculations and the reliability of the application. The test plan covers various scenarios including:

1. Trading with and without opening balances
2. Multiple currency conversions
3. Various transaction types and their tax implications
4. Edge cases in share sales and purchases
