# E-commerce Sales Analytics Dashboard

## Overview
An interactive Python dashboard for analyzing online retail transactions. It focuses on descriptive analytics, KPIs, trends, product performance, country performance, and recommended business actions.

## Dataset
Recommended dataset: UCI Machine Learning Repository — Online Retail  
https://archive.ics.uci.edu/dataset/352/online%2Bretail

The dataset contains transaction records for a UK-based non-store online retailer from 1 December 2010 to 9 December 2011. Cite the dataset source in your final submission. Do not use the exact dataset used as the internship's masterclass learning dataset.

Download `Online Retail.xlsx` from UCI and upload it in the dashboard sidebar. The app also accepts CSV files with equivalent columns.

## Features
- KPI cards: total revenue, orders, unique customers, average order value, and units sold
- Monthly revenue trend
- Top 10 countries by revenue
- Top products by revenue
- Country and customer summaries
- Date, country, and product filters
- Cleaned data table and CSV export
- Descriptive insights and recommended actions

## Important data note
The UCI Online Retail dataset has quantity and unit price but does not include product cost. Therefore, this project calculates revenue (`Quantity × UnitPrice`) and does not invent profit values.

## Files
- `app.py` — application code
- `requirements.txt` — Python dependencies
- `README.md` — project documentation and dataset source
- `Project_Report.docx` — project report with a dashboard preview

## Run locally (Windows PowerShell)
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```powershell
   python -m streamlit run app.py
   ```

6. Open the local URL shown in the terminal (usually `http://localhost:8501`).
7. Upload `Online Retail.xlsx` using the sidebar. A small illustrative demo dataset is included so you can test the app before downloading the full dataset.

## Data cleaning
- Parses transaction dates and numeric columns
- Drops rows with invalid dates or numeric values
- Excludes cancellation invoice IDs beginning with `C`
- Excludes non-positive quantities and unit prices from sales KPIs
- Calculates revenue as quantity multiplied by unit price

## KPI definitions
- Revenue = sum of quantity × unit price
- Orders = distinct invoice numbers after excluding cancellations
- Customers = distinct non-missing customer IDs
- Average Order Value = revenue / distinct orders
- Units Sold = sum of quantity

## Limitations
- Descriptive analysis does not prove causation.
- Dataset currency is GBP (£).
- The original dataset has no cost/profit field, so profit is not calculated.
- The demo data is illustrative and must not be presented as real business results.

## Suggested project report structure
1. Title and abstract
2. Problem statement and objectives
3. Dataset source and description
4. Tools and technologies
5. Data cleaning methodology
6. KPI definitions and analysis
7. Dashboard features and screenshots
8. Findings and recommended actions
9. Limitations
10. Conclusion and references
