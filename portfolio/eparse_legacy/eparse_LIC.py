import os
import re
import pandas as pd
from openpyxl import load_workbook
from eparse.core import get_df_from_file 

input_folder = "C:/Users/SAURABH/Desktop/Portfolio/data/LIC Mutual Fund"
output_path = "C:/Users/SAURABH/Desktop/Portfolio/data/LIC Mutual Fund/lic_mutual_fund_portfolio.xlsx"

class LICParser:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.amc_name = "LIC Mutual Fund"

    def clean_scheme_name(self, text):
        if not isinstance(text, str):
            return "Unknown Scheme"
        return text.split("(")[0].split("-")[0].strip()

    def is_valid_isin(self, value):
        if not isinstance(value, str):
            return False
        return value.strip().startswith("IN") and len(value.strip()) == 12

    def extract_scheme_name(self, df_gen):
        for i, df in enumerate(df_gen):
            if i == 0:
                try:
                    val = str(pd.DataFrame(df[0]).iloc[0, 0])
                    return self.clean_scheme_name(val)
                except:
                    return "Unknown Scheme"
        return "Unknown Scheme"

    def extract_table(self, df_gen):
        for i, df in enumerate(df_gen):
            df_raw = pd.DataFrame(df[0])
            if df_raw.isnull().all(axis=1).sum() >= len(df_raw) - 1:
                continue

            for j in range(len(df_raw)):
                row = df_raw.iloc[j].astype(str).str.lower()
                if any(keyword in " ".join(row) for keyword in ["name of the instrument", "isin", "industry / rating"]):
                    header = df_raw.iloc[j]
                    df_data = df_raw.iloc[j + 1:].copy()
                    df_data.columns = header
                    df_data.dropna(how="all", inplace=True)
                    return df_data.reset_index(drop=True)
        return None

    def process_file(self, file_path):
        try:
            df_gen = get_df_from_file(file_path)
            scheme_name = self.extract_scheme_name(df_gen)
            df_gen = get_df_from_file(file_path)
            df_data = self.extract_table(df_gen)

            if df_data is None:
                return None

            df_data = df_data.rename(columns={
                "Name of the Instrument": "Name of Instrument",
                "Industry / Rating": "Industry",
                "Market/Fair Value (Rounded, Rs. In Lacs)": "Market Value",
                "Rounded, % to Net Assets": "% to Net Assets",
                "YTM": "Yield"
            })

            if "ISIN" in df_data.columns:
                df_data = df_data[df_data["ISIN"].astype(str).str.startswith("IN")]

            if "Yield" not in df_data.columns:
                df_data["Yield"] = 0.0

            df_data["Coupon"] = ""

            if "% to Net Assets" in df_data.columns:
                df_data["% to Net Assets"] = (
                    pd.to_numeric(df_data["% to Net Assets"]
                    .astype(str)
                    .str.replace(r"[^\d.\-]", "", regex=True), errors="coerce") * 100
                )

            df_data["Yield"] = (
                pd.to_numeric(df_data["Yield"]
                .astype(str)
                .str.replace(r"[^\d.\-]", "", regex=True), errors="coerce")
            )

            df_data["Yield"] = df_data["Yield"].fillna("").replace(0, "")

            df_data["Type"] = df_data["Yield"].apply(
                lambda x: "Debt" if str(x).strip() not in ["", "0.0", "0"] else "Equity"
            )

            df_data["Scheme Name"] = scheme_name
            df_data["AMC"] = self.amc_name

            desired_columns = [
                "Name of Instrument", "ISIN", "Coupon", "Industry", "Quantity",
                "Market Value", "% to Net Assets", "Yield", "Type", "Scheme Name", "AMC"
            ]

            for col in desired_columns:
                if col not in df_data.columns:
                    df_data[col] = ""

            return df_data[desired_columns]

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def run(self):
        combined = []
        for file in os.listdir(self.input_dir):
            if file.endswith((".xlsx", ".xls", ".xlsb")):
                path = os.path.join(self.input_dir, file)
                print(f"Processing: {file}")
                result = self.process_file(path)
                if result is not None:
                    combined.append(result)
        if combined:
            return pd.concat(combined, ignore_index=True)
        return pd.DataFrame()

def save_output(df, output_path):
    df.to_excel(output_path, index=False)
    print(f"Saved to {output_path}")

parser = LICParser(input_folder)
result_df = parser.run()
if not result_df.empty:
    save_output(result_df, output_path)
else:
    print("No data extracted.")
