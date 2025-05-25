import re
import json
import pandas as pd
from PyPDF2 import PdfReader
from langchain.llms import Ollama

class FundFactsheetExtractor:
    def __init__(self, model_name="llama3.1"):
        """
        Initialize the extractor with an Ollama LLM instance.
        """
        self.llm = Ollama(model=model_name)
    
    @staticmethod
    def is_factsheet_page(page_text):
        """
        Determine if a page likely contains a fund factsheet using a robust keyword frequency approach.
        
        Strategy:
        - If the word "factsheet" (or close variant) is found, consider the page as a factsheet.
        - Otherwise, count occurrences of a set of fund-specific keywords.
        - If at least a threshold number of keywords appear, return True.
        """
        page_text_lower = page_text.lower()
        # Check for explicit 'factsheet'
        if "factsheet" in page_text_lower:
            return True

        # List of keywords common to fund factsheets
        keywords = [
            "fund", "nav", "fund managers", "allotment date", "investment", 
            "net asset value", "expense ratio", "exit load", "benchmark", "performance"
        ]
        
        # Count the number of keywords found in the page text
        keyword_count = sum(1 for keyword in keywords if keyword in page_text_lower)
        threshold = 3  # minimum number of keywords required
        return keyword_count >= threshold
    
    def extract_fund_details_from_text(self, text):
        """
        Use a robust prompt-based approach to extract key fund details from a given text.
        Returns the extracted details as a Python dictionary if possible.
        """
        prompt = f"""
You are a financial expert and data extraction specialist. You have been provided with a text containing a fund factsheet. Your task is to extract and summarize the key information from the factsheet.

Extract and output the following details in JSON format with these keys:
- "fund_name": Name of the fund.
- "fund_managers": List of fund managers.
- "investment_objective": The stated investment objective.
- "key_dates": Important dates mentioned (e.g., allotment date, report date).
- "performance_metrics": Any performance figures mentioned (e.g., returns, NAV).
- "fees": Details on exit load, expense ratio, etc.
- "benchmark": The benchmark index used for comparison.
- "AUM": Assets Under Management (if available).
- "risk_metrics": Any risk metrics or ratings provided.
- "fund_type": Type or category of the fund.
        

Ignore any text that is not directly relevant.

Here is the fund factsheet text:
{text}

Extract the details now.
"""
        response = self.llm.
        try:
            extracted = json.loads(response)
        except Exception:
            extracted = {"raw_response": response}
        return extracted
    
    def process_pdf(self, pdf_path):
        """
        Process the PDF file page by page. For each page that appears to be a fund factsheet,
        extract the fund details. Returns a pandas DataFrame with page numbers and the extracted details.
        """
        reader = PdfReader(pdf_path)
        results = []
        
        for i, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue  # Skip empty pages
            
            if self.is_factsheet_page(page_text):
                print(f"Processing page {i}...")
                details = self.extract_fund_details_from_text(page_text)
                results.append({"page": i, "details": details})
            else:
                print(f"Skipping page {i} as it does not appear to be a fund factsheet.")
        
        # Create a DataFrame from the results
        df = pd.DataFrame(results)
        return df

# Example usage:
if __name__ == "__main__":
    pdf_path = "/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/one.pdf"  # Replace with the actual PDF file path
    extractor = FundFactsheetExtractor(model_name="llama3.1")
    df_results = extractor.process_pdf(pdf_path)
    
    print("\nExtracted Fund Factsheet Details:")
    print(df_results)
