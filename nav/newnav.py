import pandas as pd
import os
import re
import matplotlib.pyplot as plt
from datetime import datetime

def read_mf_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Identify the starting line of actual data
    data_start_index = next(
        (i for i, line in enumerate(lines) if re.match(r'\d{6}', line.strip().split(';')[0])),
        None
    )
    
    if data_start_index is None:
        return pd.DataFrame()  # Return empty DataFrame if no valid data found
    
    # Extract actual data lines
    data_lines = lines[data_start_index:]
    
    # Process data into a list
    data = []
    for line in data_lines:
        line = line.strip()
        if line:
            parts = line.split(';')
            if len(parts) >= 8:  # Ensure correct structure
                data.append(parts)
    
    # Create a DataFrame
    columns = [
        "Scheme Code", "Scheme Name", "ISIN Div Payout/ISIN Growth", "ISIN Div Reinvestment", 
        "Net Asset Value", "Repurchase Price", "Sale Price", "Date"
    ]
    df = pd.DataFrame(data, columns=columns)
    
    # Convert relevant columns to numeric types
    df["Scheme Code"] = pd.to_numeric(df["Scheme Code"], errors='coerce')
    df["Net Asset Value"] = pd.to_numeric(df["Net Asset Value"], errors='coerce')
    df["Repurchase Price"] = pd.to_numeric(df["Repurchase Price"], errors='coerce')
    df["Sale Price"] = pd.to_numeric(df["Sale Price"], errors='coerce')
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    
    return df.dropna(subset=["Scheme Code", "Net Asset Value", "Date"])

def calculate_returns(df):
    results = []
    
    for scheme_code in df['Scheme Code'].unique():
        scheme_df = df[df['Scheme Code'] == scheme_code].copy()
        scheme_df = scheme_df.sort_values(by='Date')
        
        latest_nav = float(scheme_df['Net Asset Value'].iloc[-1])
        scheme_name = scheme_df['Scheme Name'].iloc[-1]
        
        print(f"\nProcessing scheme: {scheme_name} ({scheme_code})")
        print(f"Latest NAV: {latest_nav}")
        
        # Calculate returns for different periods
        def get_return(days):
            try:
                past_date = scheme_df['Date'].max() - pd.Timedelta(days=days)
                past_values = df[
                    (df['Scheme Code'] == scheme_code) & 
                    (df['Date'] <= past_date)
                ]['Net Asset Value']
                
                if past_values.empty:
                    return None
                    
                past_nav = float(past_values.iloc[-1])
                if past_nav == 0:
                    return None
                    
                return round(((latest_nav - past_nav) / past_nav * 100), 2)
            except Exception as e:
                print(f"Error calculating {days} day return: {str(e)}")
                return None
        
        # Calculate YTD return
        try:
            ytd_start = pd.Timestamp(scheme_df['Date'].max().year, 1, 1)
            ytd_values = df[
                (df['Scheme Code'] == scheme_code) & 
                (df['Date'] <= ytd_start)
            ]['Net Asset Value']
            
            if ytd_values.empty:
                ytd_return = None
            else:
                ytd_nav = float(ytd_values.iloc[-1])
                if ytd_nav == 0:
                    ytd_return = None
                else:
                    ytd_return = round(((latest_nav - ytd_nav) / ytd_nav * 100), 2)
        except Exception as e:
            print(f"Error calculating YTD return: {str(e)}")
            ytd_return = None
        
        # Get first available NAV for total return
        try:
            first_nav = float(scheme_df['Net Asset Value'].iloc[0])
            if first_nav == 0:
                total_return = None
            else:
                total_return = round(((latest_nav - first_nav) / first_nav * 100), 2)
        except Exception as e:
            print(f"Error calculating total return: {str(e)}")
            total_return = None
        
        result = {
            'Scheme Code': scheme_code,
            'Scheme Name': scheme_name,
            '1W Return': get_return(7),
            '1M Return': get_return(30),
            '1Y Return': get_return(365),
            '3Y Return': get_return(3 * 365),
            'YTD Return': ytd_return,
            'Total Return': total_return
        }
        
        print(f"Calculated returns: {result}")
        results.append(result)
    
    df_results = pd.DataFrame(results)
    
    # Sort by Total Return
    df_results = df_results.sort_values('Total Return', ascending=False)
    
    # Add percentage symbols after sorting
    return_columns = ['1W Return', '1M Return', '1Y Return', '3Y Return', 'YTD Return', 'Total Return']
    for col in return_columns:
        df_results[col] = df_results[col].apply(lambda x: f"{x}%" if pd.notnull(x) else x)
    
    return df_results

def create_top_performers_sheet(returns_df, writer, period_column, sheet_name, top_n=20):
    """Create a sheet with top performers for a specific time period"""
    # Create a copy and convert percentage strings back to float for sorting
    df_copy = returns_df.copy()
    df_copy[period_column] = df_copy[period_column].str.rstrip('%').astype(float)
    
    # Sort and select top performers
    top_performers = df_copy[['Scheme Code', 'Scheme Name', period_column]]\
        .sort_values(period_column, ascending=False)\
        .head(top_n)
    
    # Write to Excel
    top_performers.to_excel(writer, sheet_name=sheet_name, index=False)

def extract_amc_name(scheme_name):
    """Extract AMC name from scheme name with special handling for specific AMCs"""
    if scheme_name.startswith("Parag Parikh"):
        return "Parag Parikh"
    elif scheme_name.startswith("Aditya Birla Sun"):
        return "Aditya Birla Sun"
    else:
        return scheme_name.split(" ")[0]

def create_amc_wise_top_performers(returns_df, writer, period_column, sheet_name_prefix):
    """Create sheets for top performers of each AMC for a specific time period"""
    # Add AMC column
    df_copy = returns_df.copy()
    df_copy['AMC'] = df_copy['Scheme Name'].apply(extract_amc_name)
    
    # Convert percentage strings to float for sorting
    df_copy[period_column] = df_copy[period_column].str.rstrip('%').astype(float)
    
    # Get unique AMCs
    amcs = sorted(df_copy['AMC'].unique())
    
    # Create a summary DataFrame for all AMCs' top performers
    summary_rows = []
    
    for amc in amcs:
        # Filter for current AMC
        amc_df = df_copy[df_copy['AMC'] == amc]
        
        # Get top performer for this AMC
        top_performer = amc_df.nlargest(1, period_column)
        if not top_performer.empty:
            summary_rows.append({
                'AMC': amc,
                'Top Scheme': top_performer['Scheme Name'].iloc[0],
                'Return': f"{top_performer[period_column].iloc[0]}%"
            })
    
    # Create summary DataFrame and sort by return
    summary_df = pd.DataFrame(summary_rows)
    summary_df['Sort_Value'] = summary_df['Return'].str.rstrip('%').astype(float)
    summary_df = summary_df.sort_values('Sort_Value', ascending=False)
    summary_df = summary_df.drop('Sort_Value', axis=1)
    
    # Write summary to Excel
    sheet_name = f"{sheet_name_prefix} by AMC"
    if len(sheet_name) > 31:  # Excel sheet name length limitation
        sheet_name = sheet_name[:31]
    summary_df.to_excel(writer, sheet_name=sheet_name, index=False)

def process_multiple_files(directory):
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            print(f"\nReading file: {file_path}")
            df = read_mf_data(file_path)
            if not df.empty:
                all_data.append(df)
    
    # Combine all DataFrames into one
    if all_data:
        consolidated_df = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal records before grouping: {len(consolidated_df)}")
        
        # Sort by date and then group by Scheme Code to get latest data
        consolidated_df = consolidated_df.sort_values('Date')
        print(f"Date range in data: {consolidated_df['Date'].min()} to {consolidated_df['Date'].max()}")
        
        # Group by Scheme Code but keep all historical data for return calculations
        return consolidated_df
    return pd.DataFrame()

# Example usage
start_time = datetime.now()
print(f"Processing started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

directory_path = "C:/Users/SAURABH/Desktop/Portfolio/nav"
consolidated_df = process_multiple_files(directory_path)
print(f"\nNumber of unique schemes: {len(consolidated_df['Scheme Code'].unique())}")
returns_df = calculate_returns(consolidated_df)

# Create Excel file with multiple sheets
excel_path = os.path.join(directory_path, "mutual_fund_returns.xlsx")
with pd.ExcelWriter(excel_path) as writer:
    # Main sheet with all returns
    returns_df.to_excel(writer, sheet_name='All Returns', index=False)
    
    # Create sheets for overall top performers in each period
    period_sheets = {
        '1W Return': 'Top 1 Week',
        '1M Return': 'Top 1 Month',
        '1Y Return': 'Top 1 Year',
        '3Y Return': 'Top 3 Years',
        'YTD Return': 'Top YTD',
        'Total Return': 'Top Total Return'
    }
    
    for period_col, sheet_name in period_sheets.items():
        create_top_performers_sheet(returns_df, writer, period_col, sheet_name)
        # Create AMC-wise top performers sheet for each period
        create_amc_wise_top_performers(returns_df, writer, period_col, sheet_name)

end_time = datetime.now()
processing_time = end_time - start_time

print("\nProcessing completed!")
print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total processing time: {processing_time}")
print(f"\nExported returns to: {excel_path}")
print("The Excel file contains the following sheets:")
print("1. All Returns - Complete data for all schemes")
print("2. Top 1 Week - Overall top 20 performers for 1-week returns")
print("3. Top 1 Week by AMC - Each AMC's top performer for 1-week returns")
print("4. Top 1 Month - Overall top 20 performers for 1-month returns")
print("5. Top 1 Month by AMC - Each AMC's top performer for 1-month returns")
print("6. Top 1 Year - Overall top 20 performers for 1-year returns")
print("7. Top 1 Year by AMC - Each AMC's top performer for 1-year returns")
print("8. Top 3 Years - Overall top 20 performers for 3-year returns")
print("9. Top 3 Years by AMC - Each AMC's top performer for 3-year returns")
print("10. Top YTD - Overall top 20 performers for YTD returns")
print("11. Top YTD by AMC - Each AMC's top performer for YTD returns")
print("12. Top Total Return - Overall top 20 performers for total returns")
print("13. Top Total Return by AMC - Each AMC's top performer for total returns")
