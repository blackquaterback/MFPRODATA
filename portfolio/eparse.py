import pandas as pd


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