# RBA Exchange Rate CSV Parsing Issue Documentation

## Issue Summary
The application currently uses hardcoded exchange rates instead of parsing the RBA CSV file due to challenges with the complex structure of the CSV file.

## Current Implementation
- A hardcoded DataFrame with realistic exchange rates for major currencies (USD, EUR, JPY, GBP)
- Values set to approximate current rates: $1 AUD = $0.67 USD, €0.62 EUR, ¥95 JPY, £0.53 GBP
- Date range from 2023-01-01 to 2025-05-23 to cover all possible transaction dates

## CSV Parsing Challenges
1. **Complex Header Structure**: The RBA CSV file has multiple header rows with metadata
   - First rows contain: Title, Description, Frequency, Type, Units
   - Series ID information appears around row 10
   - Actual data starts after multiple header rows

2. **Column Mapping**: The CSV uses Series IDs (e.g., FXRUSD) instead of simple currency codes
   - Requires mapping between Series IDs and currency codes
   - Column positions may change in future file versions

3. **Date Format**: Dates in the CSV require specific parsing and validation

## Future Resolution Steps
1. Implement a robust CSV parser that:
   - Skips metadata rows (approximately first 10-15 rows)
   - Identifies the actual data header row
   - Maps Series IDs to currency codes
   - Handles date parsing and validation

2. Add comprehensive error handling and fallback mechanisms:
   - Graceful degradation if CSV format changes
   - Logging of parsing errors
   - Automatic fallback to hardcoded rates when parsing fails

3. Consider caching mechanisms:
   - Store parsed rates in a local database or cache file
   - Implement periodic updates from the RBA source

## Testing Requirements
- Create test cases with sample RBA CSV files
- Verify correct parsing of different CSV versions
- Test fallback mechanisms
- Validate currency conversion accuracy

## Resources
- RBA Exchange Rate Data: https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv
- Sample file location: `/sample_data/f11.1-data.csv`
