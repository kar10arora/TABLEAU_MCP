# Sample Datasets

This directory contains sample CSV files for testing the Tableau MCP server.

## Usage
Place your test CSV datasets here for workbook generation testing.

## Example Datasets
You can use datasets like:
- Sales data (sales.csv)
- Customer data (customers.csv)
- Product information (products.csv)
- Time-series data (metrics.csv)

## Format Requirements
- CSV format with headers
- Clean column names (no special characters)
- Mix of dimensions (text) and measures (numbers)
- Reasonable file size (<100MB for testing)

## Sample Dataset Structure

### sales.csv
```csv
date,region,category,product,sales,quantity,profit
2024-01-01,USA,Electronics,Laptop,1200,2,300
2024-01-01,UK,Furniture,Chair,450,5,120
2024-01-02,USA,Clothing,Shirt,80,4,25
```

### customers.csv
```csv
customer_id,name,segment,country
1001,John Smith,Consumer,USA
1002,Jane Doe,Corporate,UK
1003,Bob Johnson,Home Office,Canada
```
