import os
import pandas as pd
from abc import ABC, abstractmethod

class FundPortfolioParser(ABC):
    def __init__(self, datadir, amc_name):
        self.datadir = datadir
        self.amc_name = amc_name
        self.full_path = self._get_first_file_path()
        self.fund_names = self._read_index_sheet()

    def _get_first_file_path(self):
        for root, dirs, files in os.walk(self.datadir):
            for file in files:
                if file.endswith(('.xlsb', '.xls', '.xlsx')):
                    return os.path.join(root, file)
        raise FileNotFoundError("No Excel file found in the directory.")

    def _read_excel(self):
        ext = self.full_path.split(".")[-1].lower()
        if ext == "xlsb":
            return pd.read_excel(self.full_path, sheet_name=None, engine="pyxlsb", dtype=str)
        else:
            return pd.read_excel(self.full_path, sheet_name=None, dtype=str)

    def _read_index_sheet(self):
        """Override in subclass if Index sheet needed"""
        return {}

    @abstractmethod
    def _clean_sheet(self, sheet_df, fund_name):
        """Override in each subclass."""
        pass

    def process(self):
        all_sheets = self._read_excel()
        output = pd.DataFrame()

        for sheet_name, sheet_df in all_sheets.items():
            if sheet_name in self._skip_sheets():
                continue

            fund_name = self._get_fund_name(sheet_name)
            if fund_name is None:
                print(f"⚠️ Skipping sheet '{sheet_name}' – not matched to a scheme name.")
                continue

            try:
                cleaned_df = self._clean_sheet(sheet_df, fund_name)
                output = pd.concat([output, cleaned_df], ignore_index=True)
            except Exception as e:
                print(f"❌ Error processing sheet '{sheet_name}': {e}")
        return output

    def _get_fund_name(self, sheet_name):
        return self.fund_names.get(sheet_name, sheet_name)

    def _skip_sheets(self):
        return set(["Common Notes", "ESG", "Scheme"])  # Add more as needed
