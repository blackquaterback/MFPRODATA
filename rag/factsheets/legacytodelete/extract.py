import pdfplumber
import pandas as pd
import os
import re

class FundFactsheetExtractorByName:
    def __init__(self, directory, output_csv):
        self.directory = directory
        self.output_csv = output_csv
        self.fund_data = []
        # Final desired columns
        self.columns = [
            "Scheme Name", "Expense Ratio", "Inception Date", "Exit Load", 
            "Fund Manager", "Fund Objective", "Fund Type", "Risk Metric", 
            "AMC Name", "AUM (₹ Crores)", "Benchmark"
        ]
    
    def extract_details_given_fund_name(self, pdf_path, provided_fund_name):
        # Open the PDF and extract full text
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            if not full_text:
                return None
            
            # Split text into lines
            lines = full_text.split("\n")
            context_lines = []
            # Find all indices where the provided fund name occurs (case-insensitive search)
            indices = [i for i, line in enumerate(lines) if provided_fund_name.lower() in line.lower()]
            if not indices:
                print(f"Fund name '{provided_fund_name}' not found in {pdf_path}")
                return None
            
            print("fund found")
            print(indices)
            # Use the first occurrence as anchor
            anchor_index = indices[0]
            # Extract a context window around the fund name (e.g., 5 lines before and after)
            start = max(0, anchor_index - 5)
            end = min(len(lines), anchor_index + 6)
            context_lines = lines[start:end]
            context_text = "\n".join(context_lines)
            
            # Now extract attributes from the context
            details = self.extract_attributes(context_text)
            # Set the Scheme Name from provided value
            details["Scheme Name"] = provided_fund_name
            
            # Deduce AMC Name (e.g., first token from the fund name)
            details["AMC Name"] = provided_fund_name.split()[0] if provided_fund_name.split() else "N/A"
            return details

    def extract_attributes(self, text):
        # Initialize all desired columns with "N/A"
        attributes = {col: "N/A" for col in self.columns}
        # Define candidate keywords for each attribute
        keyword_map = {
            "Expense Ratio": ["Expense Ratio"],
            "Inception Date": ["Inception Date", "Allotment Date"],
            "Exit Load": ["Exit Load"],
            "Fund Manager": ["Fund Manager", "Managed by"],
            "Fund Objective": ["Investment Objective", "Scheme Objective"],
            "Fund Type": ["Type of Scheme", "Scheme Type", "Category"],
            "Risk Metric": ["Risk Level", "Risk Category"],
            "AUM (₹ Crores)": ["AUM", "Assets Under Management"],
            "Benchmark": ["Benchmark"]
        }
        # For each attribute, search line by line in the context
        lines = text.split("\n")
        for attr, keywords in keyword_map.items():
            for line in lines:
                for kw in keywords:
                    if kw.lower() in line.lower():
                        # If a colon exists, take text after colon; else take the next non-empty line.
                        if ":" in line:
                            parts = line.split(":", 1)
                            value = parts[1].strip()
                            if value:
                                attributes[attr] = value
                                break
                        else:
                            # Look at the next line if exists
                            idx = lines.index(line)
                            if idx + 1 < len(lines) and lines[idx+1].strip():
                                attributes[attr] = lines[idx+1].strip()
                                break
                if attributes[attr] != "N/A":
                    break
        return attributes

    def process_all_pdfs_with_fund_name(self, provided_fund_name):
        for filename in os.listdir(self.directory):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(self.directory, filename)
                print(f"Processing: {pdf_path} for fund '{provided_fund_name}'")
                details = self.extract_details_given_fund_name(pdf_path, provided_fund_name)
                if details:
                    self.fund_data.append(details)
        self.save_to_csv()

    def save_to_csv(self):
        df = pd.DataFrame(self.fund_data, columns=self.columns)
        df.to_csv(self.output_csv, index=False)
        print(f"Extracted data saved to {self.output_csv}")


directory='/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/'

# Example usage:
# Provide the known fund/scheme name (for example, as it appears on the factsheet)
provided_fund_name = "MIRAE ASSET MULTI ASSET ALLOCATION FUND"
extractor = FundFactsheetExtractorByName(directory,output_csv="extracted_fund_data_by_name.csv")
extractor.process_all_pdfs_with_fund_name(provided_fund_name)


