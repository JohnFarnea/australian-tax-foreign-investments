# australian-tax-foreign-investments
Caclulation of Australian Tax Liabilities on Foreign Share Trading

A web application developed in Python that allows an Australian Company to calculate its tax liability when it trades in foreign shares

For a company classified as a Trader, the rules for calculation of tax are as follows:

Gross Trading Income = Sales - Cost of Shares Sold
Cost of Shares Sold = Opening Balance of Shares + Purchases - Closing Balance of Shares
Opening Balance of Shares and Closing Balance of Shares are the Values at time of Purchase - i.e. the Cost Value
This ensures only Realised Gains are reported in Gross Trading Income

Sales Values are to be translated from the Foreign Currency to AUD at the time of the Sale Transaction
Purchases Values are to be translated from the Foreign Currency to AUD at the time of the Purchase Transaction

Functionality of the Web Site:

* Allow the User to upload a spreadsheet or CSV file containing their Opening Balance of Shares. The file should include:
  - Symbol, Quantity, Total Cost in AUD
* Allow the User to upload a spreadsheet or CSV file containing the share trades for the year. The file should include:
  - Date, Symbol, Quantity (positive for Buy and negative for sell), Unit Price, Total Gross Value (+ve or -ve), Commission (normally -ve), Net Value (+ve or -ve), Currency (ie. USD)
* Obtain ATO approved currency conversion rates from the RBA Web Site Page Here - https://www.rba.gov.au/statistics/historical-data.html#exchange-rates
* Generate a Gross Trading Income statement specifying the values as listed above in AUD
* Allow the user to drill down to a detailled view of each element of the Gross Trading Income Statement which will list the transactions including the conversion to AUD


