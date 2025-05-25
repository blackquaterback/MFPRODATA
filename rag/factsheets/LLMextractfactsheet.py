import re
import json
import pandas as pd
from PyPDF2 import PdfReader
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class FundFactsheetExtractor:
    def __init__(self, model_name="llama3.1"):
        """
        Initialize the extractor with an Ollama LLM instance wrapped inside an LLMChain.
        """
        self.llm = Ollama(model=model_name)
        # Define a prompt template for extraction. The variable {text} will be replaced with the page text.


        self.prompt_template = PromptTemplate( input_variables=["text"],
        template="""
        You are a financial expert and data extraction specialist. You have been provided with a text containing a fund factsheet. Your task is to extract and summarize the key information from the factsheet, focusing on the following attributes:

        1. "fund_name": The name of the fund.
        2. "fund_managers": A list of all fund managers.
        3. "investment_objective": The fund's investment objective.
        4. "exit_load": The exit load details, if provided.
        5. "expense_ratio": The expense ratio applicable to the fund.
        6. "benchmark": The benchmark(s) used for performance comparison.
        7. "aum": Assets Under Management (AUM) of the fund.
        8. "risk_metrics": Any risk metrics mentioned, such as volatility, Sharpe ratio, etc.
        9. "fund_type": The type of the fund (e.g., equity, debt, hybrid, etc.).

        Ignore any irrelevant information. Output your answer in valid JSON format with exactly the above keys. Here is the fund factsheet text:
        {text}

        Extract the details now.
        """
        )
        # Create the LLMChain that encapsulates the prompt and LLM
        self.extraction_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

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
        keyword_count = sum(1 for keyword in keywords if keyword in page_text_lower)
        threshold = 3  # minimum number of keywords required
        return keyword_count >= threshold
    
    def extract_fund_details_from_text(self, text):
        """
        Use the LLMChain to extract key fund details from the given text.
        Returns a Python dictionary if the chain output is valid JSON.
        """
        response = self.extraction_chain.invoke({"text": text})
        print(response)
        try:
            extracted = json.loads(response)
        except Exception:
            extracted = {"raw_response": response}
        return extracted
    
    def process_pdf(self, pdf_path):
        """
        Process the PDF file page by page. For each page that appears to be a fund factsheet,
        extract the fund details using the LLMChain. Returns a pandas DataFrame with page numbers
        and the extracted details.
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
        
        df = pd.DataFrame(results)
        return df

# Example usage:
if __name__ == "__main__":
    pdf_path = "/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/factsheet-(active-schmes-)--march-2025.pdf"  # Replace with your actual PDF file path
    extractor = FundFactsheetExtractor(model_name="llama3.1")
    df_results = extractor.process_pdf(pdf_path)
    
    print("\nExtracted Fund Factsheet Details:")
    print(df_results)
