import pandas as pd
import os
import re
import matplotlib.pyplot as plt

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
    df = df.sort_values(by='Date')
    latest_nav = df.iloc[-1]['Net Asset Value']
    scheme_name = df.iloc[-1]['Scheme Name']
    
    def get_return(days):
        past_date = df['Date'].max() - pd.Timedelta(days=days)
        past_values = df[df['Date'] <= past_date]['Net Asset Value']
        past_nav = past_values.iloc[-1] if not past_values.empty else None  # Select the latest available NAV before the date
        return ((latest_nav - past_nav) / past_nav) * 100 if past_nav else None
    
    return {
        'Scheme Name': scheme_name,
        '1M Return': get_return(30),
        '3M Return': get_return(90),
        '6M Return': get_return(180),
        'YTD Return': get_return((df['Date'].max() - pd.Timestamp(df['Date'].max().year, 1, 1)).days),
        '1Y Return': get_return(365),
        '3Y Return': get_return(3 * 365),
        '5Y Return': get_return(5 * 365)
    }

def process_multiple_files(directory):
    results = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            print("reading file", file_path)
            df = read_mf_data(file_path)
            if not df.empty:
                for scheme_code in df['Scheme Code'].unique():
                    scheme_df = df[df['Scheme Code'] == scheme_code]
                    returns = calculate_returns(scheme_df)
                    returns['Scheme Code'] = scheme_code
                    results.append(returns)
    return pd.DataFrame(results), df






# Example usage
directory_path = "/Users/njp60/Documents/code/mutualfundbackend/funddata/data/nav"  # Replace with the actual directory path
returns, df = process_multiple_files(directory_path)


print(returns.head(50))




"""


def find_top_fund_by_scheme(returns_df, scheme_keyword, period='1Y Return'):
    scheme_funds = returns_df[returns_df['Scheme Name'].str.contains(scheme_keyword, case=False, na=False)]
    top_fund = scheme_funds.sort_values(by=period, ascending=False).head(20)
    return top_fund

# Example usage
top_fund = find_top_fund_by_scheme(returns, scheme_keyword="HDFC", period='1Y Return')  # Change scheme name and period as needed
print(top_fund)

# Example usage
top_fund = find_top_fund_by_scheme(returns, scheme_keyword="ICICI", period='1Y Return')  # Change scheme name and period as needed
print(top_fund)


# Example usage
top_fund = find_top_fund_by_scheme(returns, scheme_keyword="Axis", period='1Y Return')  # Change scheme name and period as needed
print(top_fund)

# Example usage
top_fund = find_top_fund_by_scheme(returns, scheme_keyword="One", period='1Y Return')  # Change scheme name and period as needed
print(top_fund)

top_fund = find_top_fund_by_scheme(returns, scheme_keyword="flexi", period='1Y Return')  # Change scheme name and period as needed
print(top_fund)




def plot_fund_timeseries(df, scheme_code):
    #Plot NAV time series for a specific fund identified by Scheme Code.
    fund_df = df[df["Scheme Code"] == scheme_code].sort_values(by="Date")

    if fund_df.empty:
        print(f"No data found for Scheme Code {scheme_code}")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(fund_df["Date"], fund_df["Net Asset Value"], marker="o", linestyle="-", label=fund_df.iloc[0]["Scheme Name"])
    
    plt.xlabel("Date")
    plt.ylabel("Net Asset Value (NAV)")
    plt.title(f"Time Series of NAV for {fund_df.iloc[0]['Scheme Name']} ({scheme_code})")
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
#plot_fund_timeseries(df, scheme_code="118955")  # Replace with the actual Scheme Code
"""
