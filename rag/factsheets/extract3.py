import pdfplumber
import pandas as pd
import os
import re

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
            relevant_pages = []
            full_text = []
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                full_text.append(text)
                if self.provided_fund_name in text.lower():
                    relevant_pages.append(i)
                    print(f"Fund found at page: {i}")
                    details=self.extract_attributes(text)
                    print(details)


            
            # Process only the relevant pages
            extracted_details = self.process_relevant_pages(pdf, relevant_pages, full_text)
            
            if extracted_details:
                extracted_details["Scheme Name"] = self.provided_fund_name.title()
                self.fund_data.append(extracted_details)
    
    def process_relevant_pages(self, pdf, relevant_pages, full_text):
        details = {col: "N/A" for col in self.columns}
        
        for page_index in relevant_pages:
            text = full_text[page_index]
            extracted_info = self.extract_attributes(text)
            for key in extracted_info:
                if extracted_info[key] != "N/A":
                    details[key] = extracted_info[key]
        
        return details
    
    def extract_attributes2(self, text):
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
    
    def extract_attributes(self, text):
        details = {col: "N/A" for col in self.columns}
        
        attributes = {
            "AUM (₹ Crores)": r"(?:AUM|Assets Under Management)[^\d]*([\d,]+\.?\d*)",
            "Fund Manager": r"(?:Fund Manager|Managed by):?\s*([\w\s,]+)",
            "Expense Ratio": r"(?:Expense Ratio):?\s*([\d.]+%)",
            "Exit Load": r"(?:Exit Load):?\s*(.*?)(?:\n|$)",
            "Inception Date": r"(?:Inception Date|Launched on):?\s*([\w\s,]+)",
            "Benchmark": r"(?:Benchmark|Index):?\s*(.*?)(?:\n|$)",
            "Risk Level": r"(?:Risk Level|Risk Category):?\s*([\w\s]+)",
            "Type of Fund": r"(?:Type|Category|Fund Type):?\s*(.*?)(?:\n|$)"
        }

        # Normalize spacing for better matching
        text = " ".join(text.split())

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




provided_fund_name = "MIRAE ASSET MULTI ASSET ALLOCATION FUND"

directory='/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/'
extractor = FundFactsheetExtractor(directory=directory, output_csv="extracted_fund_data.csv", provided_fund_name=provided_fund_name)
extractor.process_all_pdfs()
