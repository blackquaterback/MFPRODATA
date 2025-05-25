import pdfplumber
import re
import os
import pandas as pd
from fuzzywuzzy import fuzz  # Fuzzy matching

class FundFactsheetExtractorByName:
    def __init__(self, directory, output_csv, provided_fund_name):
        self.directory = directory
        self.output_csv = output_csv
        self.provided_fund_name = provided_fund_name
        self.fund_data = []
        self.columns = [
            "Scheme Name", "Expense Ratio", "Inception Date", "Exit Load", 
            "Fund Manager", "Fund Objective", "Fund Type", "Risk Metric", 
            "AMC Name", "AUM (₹ Crores)", "Benchmark"
        ]

    def extract_fund_details_from_pdf(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            full_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.extend(text.split("\n"))
        
        # Find all occurrences of the fund name
        indices = [i for i, line in enumerate(full_text) if provided_fund_name.lower() in line.lower()]

        if not indices:
            print(f"Fund '{self.provided_fund_name}' not found in {pdf_path}")
            return
        
        print(f"Fund found at indices: {indices}")

        # Extract details for each occurrence and pick the best
        best_details = None
        best_score = -1

        for idx in indices:
            context = self.get_context(full_text, idx)
            details = self.extract_attributes(context)
            

            print(f" CONTEXT found at indices: {idx}")

            print(context)


            # Scoring: Count non-empty attributes
            score = sum(1 for v in details.values() if v != "N/A")

            if score > best_score:
                best_score = score
                best_details = details

        if best_details:
            best_details["Scheme Name"] = self.provided_fund_name
            self.fund_data.append(best_details)

    def get_context(self, lines, index, window=8):
        """ Extract a dynamic window around the given index """
        start = max(0, index - window)
        end = min(len(lines), index + window)
        return "\n".join(lines[start:end])

    def extract_attributes(self, text):
        """ Extract required attributes from the context """
        details = {col: "N/A" for col in self.columns}

        attributes = {
            "Expense Ratio": r"Expense Ratio:?\s*([\d.]+%)",
            "Inception Date": r"Inception Date:?\s*([\w\s\d,]+)",
            "Exit Load": r"Exit Load:?\s*(.+)",
            "Fund Manager": r"Fund Manager:?\s*(.+)",
            "Fund Objective": r"Objective:?\s*(.+)",
            "Fund Type": r"Fund Type:?\s*(.+)",
            "Risk Metric": r"Risk(?: Level)?:?\s*(.+)",
            "AMC Name": r"AMC:?\s*(.+)",
            "AUM (₹ Crores)": r"AUM:?\s*([\d,]+\.?\d*)",
            "Benchmark": r"Benchmark:?\s*(.+)"
        }

        for key, pattern in attributes.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details[key] = match.group(1).strip()

        return details

    def process_all_pdfs(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.directory, filename)
                print(f"Processing: {pdf_path}")
                self.extract_fund_details_from_pdf(pdf_path)
        
        self.save_to_csv()

    def save_to_csv(self):
        df = pd.DataFrame(self.fund_data, columns=self.columns)
        df.to_csv(self.output_csv, index=False)
        print(f"Extracted data saved to {self.output_csv}")

directory='/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/'
provided_fund_name = "MIRAE ASSET MULTI ASSET ALLOCATION FUND"
extractor = FundFactsheetExtractorByName(directory,"extracted_fund_data_by_name.csv",provided_fund_name)
extractor.process_all_pdfs()
