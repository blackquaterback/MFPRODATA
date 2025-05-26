import pandas as pd
import os


# This function is designed to clean and process the data from Parag Parikh Mutual Fund's portfolio sheets adapated from eparse_parag_parikh.py in legacy folder 
# Create similar functions for other AMCs 

def clean_parag_parikh(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
 

    full_data=pd.DataFrame()

    for sheet_name, sheet_df in df_raw.items():
                    
            if sheet_name not in sheets_to_avoid:
                    print(f"\n🔍 Processing  → Sheet: {sheet_name}")

                    fund = fund_names.get(sheet_name, None)

                    if fund is not None and sheet_name:
                        print(f"\n🔍 Processing  → Sheet: {fund}")


                        header_row_idx = next(
                            (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                            None
                        )
                        if header_row_idx is None:
                            print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                            continue

                        df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                        df_clean.columns = df_clean.iloc[0]
                        df_clean = df_clean[1:].reset_index(drop=True)

                        df_clean= df_clean.loc[:, df_clean.columns.notna()]

                        print(df_clean.head(10))

                        df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value (Rs.in Lacs)", "% to Net Assets", "Yield", "Yield 2"]
                        df_clean = df_clean.rename(columns={"Market Value (Rs.in Lacs)": "Market Value"})
                        df_clean = df_clean.drop(columns=["Yield 2"])
                    

                        df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)

                                    #Just a simple logic to determine the type of instrument need to update later TODO

                        df_clean[['Yield']] = df_clean[['Yield']].fillna(value=0)
                        df_clean['Type'] = df_clean['Yield'].apply(lambda x: 'Debt or related' if x != 0 else 'Equity or Equity related')


                        df_clean = df_clean.round(2)
                        df_clean["Scheme Name"] = fund
                        df_clean["AMC"] = AMC_NAME
                        full_data=pd.concat([full_data,df_clean],ignore_index=True) if not full_data.empty else df_clean



    full_data.to_excel(output_file, index=False)

def clean_icici(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_mirae(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = 'Equity or Equity related'  # Mirae is primarily equity focused
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_quant(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_sbin(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_nippon(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_axis(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_kotak(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_hdfc(df_raw, fund_names, sheets_to_avoid, AMC_NAME, datafile, output_file):
    full_data = pd.DataFrame()
    
    for sheet_name, sheet_df in df_raw.items():
        if sheet_name not in sheets_to_avoid:
            print(f"\n🔍 Processing  → Sheet: {sheet_name}")
            fund = fund_names.get(sheet_name, None)
            
            if fund is not None and sheet_name:
                print(f"\n🔍 Processing  → Sheet: {fund}")
                
                header_row_idx = next(
                    (index for index, row in sheet_df.iterrows() if any("ISIN" in str(val) for val in row.dropna())),
                    None
                )
                if header_row_idx is None:
                    print(f"⚠️ Skipping {sheet_name} (No ISIN header found)")
                    continue

                df_clean = pd.read_excel(datafile, sheet_name=sheet_name, skiprows=header_row_idx, dtype=str)
                df_clean.columns = df_clean.iloc[0]
                df_clean = df_clean[1:].reset_index(drop=True)
                df_clean = df_clean.loc[:, df_clean.columns.notna()]

                df_clean.columns = ["Name of Instrument", "ISIN", "Industry", "Quantity", "Market Value", "% to Net Assets"]
                df_clean.dropna(subset=["ISIN", "Name of Instrument", "Market Value"], inplace=True)
                
                df_clean['Type'] = df_clean['Industry'].apply(lambda x: 'Debt or related' if 'DEBT' in str(x).upper() else 'Equity or Equity related')
                
                df_clean = df_clean.round(2)
                df_clean["Scheme Name"] = fund
                df_clean["AMC"] = AMC_NAME
                full_data = pd.concat([full_data, df_clean], ignore_index=True) if not full_data.empty else df_clean

    full_data.to_excel(output_file, index=False)
    return full_data

def clean_canara(sheet_df, fund_name, full_path):
    df_raw = sheet_df.copy()
    df_raw.dropna(how="all", inplace=True)
    df_raw.columns = df_raw.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    df_raw.rename(columns={
        "Name of the Instrument": "Name of Instrument",
        "Market/Fair Value (Rs. in Lacs)": "Market Value",
        "% to Net Assets": "% to Net Assets",
        "Yield %": "Yield",
        "Industry / Rating": "Industry",
        "Market Capitalization": "Market Capitalization"
    }, inplace=True)

    if "ISIN" in df_raw.columns:
        isin_idx = df_raw.columns.get_loc("ISIN")
        df_raw.insert(isin_idx + 1, "Coupon", "")
    else:
        df_raw["Coupon"] = ""

    if "% to Net Assets" in df_raw.columns:
        df_raw["% to Net Assets"] = (
            df_raw["% to Net Assets"]
            .astype(str)
            .str.replace(r"[^\d.\-]", "", regex=True)
            .replace("", "0")
            .astype(float)
        )

    if "Yield" in df_raw.columns:
        df_raw["Yield"] = (
            df_raw["Yield"]
            .astype(str)
            .str.replace(r"[^\d.\-]", "", regex=True)
            .replace("", "0")
            .astype(float)
        )
    else:
        df_raw["Yield"] = 0.0

    df_raw["Yield"] = df_raw["Yield"].replace(0, "")
    df_raw["Type"] = df_raw["Yield"].apply(lambda x: "Debt" if pd.notna(x) and x != "" else "Equity")

    df_raw["Scheme Name"] = fund_name
    df_raw["AMC"] = "Canara Robeco Mutual Fund"

    required_columns = [
        "Name of Instrument", "ISIN", "Coupon", "Industry", "Quantity",
        "Market Value", "% to Net Assets", "Market Capitalization", "Yield",
        "Type", "Scheme Name", "AMC"
    ]

    for col in required_columns:
        if col not in df_raw.columns:
            df_raw[col] = ""

    df_final = df_raw[required_columns]
    df_final = df_final[df_final["ISIN"].astype(str).str.startswith("IN", na=False)]
    df_final = df_final.drop(columns=["Market Capitalization"], errors="ignore")
    return df_final
