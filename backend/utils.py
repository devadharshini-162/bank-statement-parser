import pandas as pd
import json
import os
from datetime import datetime
from openpyxl.styles import Font

def transactions_to_dataframe(transactions):
    """
    Takes a list of dictionary transactions and converts them to a Pandas DataFrame.
    Cleans up whitespace from strings and ensures financial columns are properly converted to numeric types.
    """
    # Convert list of dicts to a DataFrame
    df = pd.DataFrame(transactions)
    
    if df.empty:
        return df

    # Clean string columns (e.g. date, description)
    for col in df.columns:
        if df[col].dtype == "object":
            # Strip whitespace, handling None/NaN values gracefully
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            
    # Convert financial columns to numeric using pd.to_numeric
    # errors='coerce' forces invalid data to NaN instead of failing
    num_cols = ['debit', 'credit', 'balance']
    for col in num_cols:
        if col in df.columns:
            # Optional: Strip out commas and '$' signs before converting
            if df[col].dtype == "object":
                df[col] = df[col].replace(r'[\$,]', '', regex=True)
                
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def save_to_excel(dataframe, output_path):
    """
    Saves a Pandas DataFrame to an Excel file using the openpyxl engine.
    Automatically applies basic formatting like bold headers and adjusts column widths.
    """
    # Open an Excel writer with openpyxl
    writer = pd.ExcelWriter(output_path, engine='openpyxl')
    
    # Write the raw dataframe Data
    dataframe.to_excel(writer, sheet_name='Transactions', index=False)
    
    # Access the workbook sheet to apply formatting
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        
        # Enumerate over columns to format the header and set widths
        # openpyxl is 1-indexed for row/column coordinates
        for col_idx, column_title in enumerate(dataframe.columns, 1):
            
            # Make the header row bold
            cell = worksheet.cell(row=1, column=col_idx)
            cell.font = Font(bold=True)
            
            # Calculate the max length of data in this column to set the width
            # We map strings to length and find max. If column is empty, handle carefully
            try:
                # Handle potential float NaNs by filling with empty string first
                col_series = dataframe[column_title].fillna('')
                max_val = col_series.astype(str).map(len).max()
                
                # If dataframe has 0 rows, max() returns NaN
                if pd.isna(max_val):
                    max_len = len(str(column_title))
                else:
                    max_len = max(int(max_val), len(str(column_title)))
            except ValueError:
                max_len = len(str(column_title))
                
            # Grab the column letter (e.g., 'A', 'B', 'C')
            col_letter = worksheet.cell(row=1, column=col_idx).column_letter
            
            # Auto-adjust column width based on max content length + padding
            worksheet.column_dimensions[col_letter].width = max_len + 2

    # Save and close
    writer.close()
    
    return output_path

def validate_transactions(dataframe):
    """
    Validates transaction logic and calculates sums.
    It returns total debits, total credits, flags anomalies (like empty debit and credit,
    or negative balances), and sets an is_valid boolean flag.
    """
    if dataframe.empty:
        return {
            "total_debits": 0,
            "total_credits": 0,
            "anomalies": [],
            "is_valid": True
        }

    # Calculate total debits and credits, ignoring NaNs
    total_debits = dataframe['debit'].sum(skipna=True) if 'debit' in dataframe else 0
    total_credits = dataframe['credit'].sum(skipna=True) if 'credit' in dataframe else 0
    
    anomalies = []
    
    # Iterate over rows to validate transaction logic
    for index, row in dataframe.iterrows():
        # Check if both debit and credit are missing
        has_no_debit = pd.isna(row.get('debit'))
        has_no_credit = pd.isna(row.get('credit'))
        
        if has_no_debit and has_no_credit:
            anomalies.append(index)
            
        # Check if the balance is negative (often an anomaly in statements)
        if 'balance' in row and not pd.isna(row.get('balance')) and row.get('balance') < 0:
            # avoid duplicates if already flagged
            if index not in anomalies:
                anomalies.append(index)

    return {
    "total_debits": float(total_debits) if total_debits else 0.0,
    "total_credits": float(total_credits) if total_credits else 0.0,
    "anomalies": list(anomalies) if anomalies else [],
    "is_valid": len(anomalies) == 0
}

def generate_output_filename(original_filename):
    """
    Creates a timestamped output filename natively from an original PDF file name.
    Format is: parsed_ORIGINALNAME_YYYYMMDD_HHMMSS.xlsx
    """
    # Extract the base filename without its extension
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    
    # Get the current time formatting string
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Return the new filename string
    return f"parsed_{base_name}_{timestamp}.xlsx"
