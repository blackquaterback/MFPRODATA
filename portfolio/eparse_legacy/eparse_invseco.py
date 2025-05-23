import os
import pandas as pd

class InvescoMutualFundParser:
    def __init__(self, folder_path, amc_name="Invesco Mutual Fund"):
        self.folder_path = folder_path
        self.amc_name = amc_name

    def clean_scheme_name(self, text):
        if not isinstance(text, str):
            return "Unknown Scheme"
        if "India" in text and "Fund" in text:
            return text.split("India", 1)[-1].split("Fund", 1)[0].strip() + " Fund"
        return "Unknown Scheme"

    def parse_file(self, file_path):
        try:
            df_raw = pd.read_excel(file_path, sheet_name=0, header=None)

            investment_type = df_raw.iloc[5, 1] if df_raw.shape[0] > 5 else None
            scheme_text = df_raw.iloc[2, 1] if df_raw.shape[0] > 2 else ""
            scheme_name = self.clean_scheme_name(scheme_text)

            headers = df_raw.iloc[4, 1:8].tolist()
            df_data = df_raw.iloc[7:, 1:8].copy()
            df_data.columns = headers
            df_data.dropna(how="all", inplace=True)

            remove_keywords = ["Equity & Equity related", "awaiting listing", "Sub Total", "Grand Total"]
            df_data = df_data[~df_data["Name of the Instrument"].astype(str).str.contains('|'.join(remove_keywords), case=False, na=False)]

            df_data.rename(columns={
                "Name of the Instrument": "Name of Instrument",
                "Industry*": "Industry",
                "Market/Fair Value (Rs. in Lakhs)": "Market Value",
                "YTM": "Yield"
            }, inplace=True)

            df_data["Type"] = investment_type
            df_data["Scheme Name"] = scheme_name
            df_data["AMC"] = self.amc_name

            return df_data

        except Exception as e:
            print(f"Failed to process {file_path}: {e}")
            return None

    def run(self):
        combined_data = []
        files = [f for f in os.listdir(self.folder_path) if f.endswith(('.xlsx', '.xls'))]

        for file in files:
            file_path = os.path.join(self.folder_path, file)
            print(f"Processing: {file}")
            df = self.parse_file(file_path)
            if df is not None:
                combined_data.append(df)

        if combined_data:
            df_all = pd.concat(combined_data, ignore_index=True)

            df_all = df_all[
                ~(
                    df_all["% to Net Assets"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(["", "nil"])
                    |
                    df_all["Name of Instrument"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains("total")
                )
            ]

            cols = list(df_all.columns)
            if "ISIN" in cols:
                isin_idx = cols.index("ISIN")
                cols.insert(isin_idx + 1, "Coupon")
            else:
                cols.insert(2, "Coupon")
            df_all["Coupon"] = ""
            df_all = df_all.reindex(columns=cols)

            return df_all
        return pd.DataFrame()

def save_to_excel(df, output_path):
    df.to_excel(output_path, index=False)
    print(f"Saved to {output_path}")

input_folder = "C:/Users/SAURABH/Desktop/Portfolio/data/Invesco Mutual Fund"
output_file = "C:/Users/SAURABH/Desktop/Portfolio/data/Invesco Mutual Fund/invesco_mutualfund.xlsx"
parser = InvescoMutualFundParser(input_folder)
result_df = parser.run()
if not result_df.empty:
    save_to_excel(result_df, output_file)
else:
    print("No valid data extracted.")
