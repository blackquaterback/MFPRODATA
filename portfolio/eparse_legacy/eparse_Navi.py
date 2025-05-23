
import os
import pandas as pd
import re

parser = NaviMutualFundParser("C:\Users\SAURABH\Desktop\Portfolio\data\Navi Mutual Fund")

class NaviMutualFundParser:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.amc_name = "Navi Mutual Fund"

    def clean_scheme_name(self, name):
        if not isinstance(name, str):
            return "Unknown Scheme"
        return name.split("(")[0].split("-")[0].strip()

    def parse_file(self, file_path):
        try:
            df_raw = pd.read_excel(file_path, sheet_name=0, header=None)
            scheme_name = self.clean_scheme_name(df_raw.iloc[4, 0]) if df_raw.shape[0] > 4 else "Unknown Scheme"

            headers = df_raw.iloc[6].astype(str).str.strip()
            df_data = df_raw.iloc[7:].copy()
            df_data.columns = headers
            df_data.dropna(how="all", inplace=True)

            df_data = df_data.rename(columns={
                'Name of the Instrument': 'Name of Instrument',
                'Industry/Rating': 'Industry',
                'Market/Fair Value (Rs. in Lacs)': 'Market Value',
                'YIELD': 'Yield',
                'Quantity\n(Market or Face Value)': 'Quantity'
            })

            if 'ISIN' in df_data.columns:
                isin_index = list(df_data.columns).index("ISIN")
                df_data.insert(isin_index + 1, "Coupon", "")
            else:
                df_data["Coupon"] = ""

            if "% to Net Assets" in df_data.columns:
                df_data = df_data[df_data["% to Net Assets"].notna()]
                df_data = df_data[df_data["% to Net Assets"].astype(str).str.strip().str.lower() != "nil"]

            first_col = df_data.columns[0]
            df_data = df_data[~df_data[first_col].astype(str).str.contains("Total", case=False, na=False)]

            df_data["Scheme Name"] = scheme_name
            df_data["AMC"] = self.amc_name
            df_data["Type"] = df_data.get("Yield", "").apply(
                lambda x: "Debt" if pd.notna(x) and str(x).strip() != "" else "Equity"
            )

            expected_columns = [
                "Name of Instrument", "ISIN", "Coupon", "Industry", "Quantity",
                "Market Value", "% to Net Assets", "Yield", "Type", "Scheme Name", "AMC"
            ]
            for col in expected_columns:
                if col not in df_data.columns:
                    df_data[col] = ""
            return df_data[expected_columns]

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return None

    def run(self):
        all_data = []
        for filename in os.listdir(self.input_dir):
            if filename.endswith((".xlsx", ".xls")):
                file_path = os.path.join(self.input_dir, filename)
                print(f"Processing: {filename}")
                df = self.parse_file(file_path)
                if df is not None:
                    all_data.append(df)
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()

def save_to_excel(df, output_file):
    df.to_excel(output_file, index=False)
    print(f"Output saved to: {output_file}")

result = parser.run()
if not result.empty:
    save_to_excel(result, "navi_fund_portfolio.xlsx")
else:
    print("No data extracted.")
