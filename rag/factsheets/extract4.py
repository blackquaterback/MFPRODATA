import pdfplumber
import pandas as pd
import os
import re
from unstructured.partition.pdf import partition_pdf

class FundFactsheetExtractor:
    def __init__(self, directory, output_csv, provided_fund_name):
        self.directory = directory
        self.output_csv = output_csv
        self.provided_fund_name = provided_fund_name.lower()
        self.fund_data = []
        self.columns = [
            "Scheme Name", "AUM (₹ Crores)", "Fund Manager", "Expense Ratio", 
            "Exit Load", "Inception Date", "Benchmark", "Risk Level", "Type of Fund"
        ]

    def extract_fund_details_from_pdf(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            full_text = []
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                full_text.append(text)
                if self.provided_fund_name in text.lower():
                    print(f"Processing relevant page {i+1} of {pdf_path}...")
                    
                    # Step 1: Process the page with unstructured
                    extracted_text = self.process_page_with_unstructured(pdf_path, i+1)
                    
                    # Step 2: Extract attributes
                    extracted_details = self.extract_attributes(extracted_text)
                    extracted_details["Scheme Name"] = self.provided_fund_name.title()
                    self.fund_data.append(extracted_details)
    
    def process_page_with_unstructured(self, pdf_path, page_number):
        """Extracts text using unstructured for better table and data extraction."""
        elements = partition_pdf(filename=pdf_path, pages=[page_number])
        return " ".join([el.text for el in elements if hasattr(el, "text")])

    def extract_attributes(self, text):
        """Extracts key attributes from text using regex patterns."""
        details = {col: "N/A" for col in self.columns}
        
        attributes = {
            "AUM (₹ Crores)": r"(?:AUM|Assets Under Management)[^\d]*([\d,]+\.?\d*)",
            "Fund Manager": r"(?:Fund Manager|Managed by):?\s*(.+)",
            "Expense Ratio": r"(?:Expense Ratio):?\s*([\d.]+%)",
            "Exit Load": r"(?:Exit Load):?\s*(.+)",
            "Inception Date": r"(?:Inception Date):?\s*(.+)",
            "Benchmark": r"(?:Benchmark):?\s*(.+)",
            "Risk Level": r"(?:Risk Level|Risk Category):?\s*(.+)",
            "Type of Fund": r"(?:Type|Category):?\s*(.+)"
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
                print(f"Scanning {pdf_path} for fund details...")
                self.extract_fund_details_from_pdf(pdf_path)
        
        self.save_to_csv()

    def save_to_csv(self):
        df = pd.DataFrame(self.fund_data, columns=self.columns)
        df.to_csv(self.output_csv, index=False)
        print(f"Extracted data saved to {self.output_csv}")

provided_fund_name = "MIRAE ASSET MULTI ASSET ALLOCATION FUND"
directory='/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/'
extractor = FundFactsheetExtractor(directory=directory, output_csv="extracted_fund_data.csv", provided_fund_name=provided_fund_name)
extractor.process_all_pdfs()
