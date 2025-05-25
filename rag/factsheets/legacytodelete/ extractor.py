
# Define the file path
file_path = "/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/NAVAll.txt"
pdf="/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/factsheet1.pdf"


import pandas as pd
import re
import fitz  # PyMuPDF
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

import pdfplumber

def extract_tables_from_page(pdf_path, page_number):
    tables = []
    print(pdf_path)
    with pdfplumber.open(pdf_path) as pdf:
        if page_number <= len(pdf.pages):  # Check if page exists
            page = pdf.pages[page_number - 1]  # 0-based index
            extracted_tables = page.extract_tables()
            
            if extracted_tables:
                print(f"📊 {len(extracted_tables)} tables found on page {page_number}")
                tables = extracted_tables
            else:
                print(f"⚠️ No tables found on page {page_number}")

    return tables

# Example Usage:
pdf_file = "example.pdf"
page_num = 2  # Change to the page number you want to extract tables from
tables = extract_tables_from_page(pdf_file, page_num)

for idx, table in enumerate(tables):
    print(f"\n🏷 Table {idx + 1} on Page {page_num}:")
    for row in table:
        print(row)


def extract_mutual_fund_details_ollama(text, fund_name, model_name="llama3"):
    """
    Extract mutual fund details from a PDF using LangChain with an Ollama-hosted LLaMA 3.1 model.
    
    Args:
        pdf_path (str): Path to the mutual fund PDF.
        fund_name (str): The name of the mutual fund to search for in the document.
        model_name (str): The Ollama model name (default is "llama3").
    
    Returns:
        list: Extracted mutual fund details in JSON format.
    """
    
    # Split text for better processing
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    # Initialize Ollama LLM with LLaMA 3.1
    llm = Ollama(model=model_name)

    # Define Prompt Template
    prompt_template = PromptTemplate(
        input_variables=["text", "fund_name"],
        template="""
        Extract details for the mutual fund named "{fund_name}" from the given text.
        
        Required details:
        - Fund Name
        - AMC (Asset Management Company)
        - Expense Ratio (Direct & Regular Plans)
        - Inception Date
        - Exit Load
        - Fund Manager(s)
        - Fund Objective
        - Fund Type (Equity, Debt, Hybrid, etc.)
        - Risk Level (Riskometer)

        Text:
        {text}

        Provide a structured JSON response:
        {{
            "Fund Name": "{fund_name}",
            "AMC Name": "...",
            "Expense Ratio": {{"Direct": "...%", "Regular": "...%"}},
            "Inception Date": "...",
            "Exit Load": "...",
            "Fund Manager": ["...", "..."],
            "Fund Objective": "...",
            "Fund Type": "...",
            "Risk Level": "..."
        }}
        """
    )

    # Create LangChain LLM Chain
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Process each chunk and extract results
    extracted_data = []
    for chunk in chunks:
        response = chain.run(text=chunk, fund_name=fund_name)
        extracted_data.append(response)

    return extracted_data



def is_factsheet_page(text):
    """
    Improved function to determine if a page is part of the mutual fund factsheet.
    
    Args:
        text (str): Extracted text from the PDF page.
    
    Returns:
        bool: True if the page is a factsheet page, False otherwise.
    """
    # Keywords commonly found on factsheet pages

    # Keywords commonly found on factsheet pages
    keywords = [
        "Fund Factsheet", "Investment Objective", "Portfolio Snapshot",
        "Top Holdings", "NAV", "Returns", "Fund Manager", "Sector Allocation"
    ]
    
    # Check if at least two keywords appear
    keyword_count = sum(1 for keyword in keywords if keyword.lower() in text.lower())
    
    # Regular expression to detect NAV values (e.g., "1234.56", "10.25%")
    nav_pattern = r"\b\d{3,4}\.\d{2}\b"  # Matches NAV-like numbers
    percentage_pattern = r"\b\d{1,2}\.\d{2}%\b"  # Matches percentage allocations
    
    # If at least two keywords and at least 2 NAV or percentage values are found, it's a factsheet
    if keyword_count >= 2 and (len(re.findall(nav_pattern, text)) >= 2 or len(re.findall(percentage_pattern, text)) >= 2):
        return True
    
    return False


def extract_text_with_fund(pdf_file, fund_name):
    doc = fitz.open(pdf_file)
    extracted_data = {}
    extracted_text = ""


    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        
        if fund_name.lower() in text.lower():  # Case-insensitive search
            extracted_data[page_num + 1] = text  # Store page number and text
            extracted_text += text + "\n"
    return extracted_text.strip()

def extract_text_and_tables(pdf_path, target_page=None):
    """Extract text and tables from a PDF. Optionally extract from a specific page."""
    text_data = {}
    table_data = {}

    print(f"Extracting text and tables from PDF: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if target_page and page_num != target_page:
                continue  # Skip pages if a specific page is requested

            extracted_text = page.extract_text()
            extracted_tables = page.extract_tables()

            if extracted_text:
                text_data[page_num] = extracted_text
                print(f"Extracted text from page {page_num}")

            if extracted_tables:
                table_data[page_num] = extracted_tables
                print(f"Extracted {len(extracted_tables)} table(s) from page {page_num}")

    print("Text and table extraction completed.")
    return text_data, table_data



def extract_text_from_pdf(self, pdf_path):
    """Extract text from PDF and include page numbers."""
    text_data = {}
    print(f"Extracting text from PDF: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            extracted_text = page.extract_text()
            if extracted_text:
                text_data[page_num] = extracted_text  # Store text with page number
                print(f"Extracted text from page {page_num}")

    print("Text extraction completed.")
    return text_data


def find_fund_pages(pdf_path, fund_names):
    """
    Reads a mutual fund factsheet and returns page numbers where each fund name appears.
    
    Args:
        pdf_path (str): Path to the PDF factsheet.
        fund_names (list): List of fund names to search for.

    Returns:
        dict: A dictionary with fund names as keys and a list of page numbers as values.
    """
    fund_pages = {fund: [] for fund in fund_names}  # Initialize empty lists for each fund
    
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Iterate through pages
    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")  # Extract text from the page

        extracted_data = {}
        extracted_text = ""

        

        # Check if any fund name appears in the page
        if is_factsheet_page(text):  # Check if the page is a factsheet
            print(f"Processing factsheet {page_num + 1}...")
            for fund in fund_names:
                if fund.lower() in text.lower():
                    fund_pages[fund].append(page_num + 1)  # Store 1-based page numbers
                    extracted_data[page_num + 1] = text 
                    extracted_text += text + "\n"

    doc.close()
    return fund_pages, extracted_text.strip(), extracted_data

def clean_fund_name(name):
    """Removes anything after 'Fund' in the given scheme name."""
    return re.sub(r"(FUND).*", r"\1", name)


def is_factsheet_page2(page_text):
        """
        Determine if a page likely contains a fund factsheet using a robust keyword frequency approach.
        
        Strategy:
        - If the word "factsheet" (or close variant) is found, consider the page as a factsheet.
        - Otherwise, count occurrences of a set of fund-specific keywords.
        - If at least a threshold number of keywords appear, return True.
        """
        page_text_lower = page_text.lower()
        # Check for explicit 'factsheet'
        if "monthly factsheet" in page_text_lower:
            return True

        # List of keywords common to fund factsheets
        keywords = [
            "fund", "nav", "fund managers", "allotment date", "investment", 
            "net asset value", "expense ratio", "exit load", "benchmark", "performance"
        ]
        keyword_count = sum(1 for keyword in keywords if keyword in page_text_lower)
        threshold = 6  # minimum number of keywords required
        return keyword_count >= threshold

# Define column headers
column_names = [
    "Scheme Code", "ISIN Div Payout", "ISIN Growth",
    "Scheme Name", "Net Asset Value", "Date"
]

# Read the file into a DataFrame
df = pd.read_csv(file_path, sep=";", dtype=str, engine="python", names=column_names, header=None, skiprows=1)


df.dropna(subset=["Scheme Name"], inplace=True)

# Display the first few rows

# Print column count for validation
print(f"Number of columns detected: {df.shape[1]}")
fundnames=df['Scheme Name'].copy().apply(clean_fund_name).unique()


processing_list=[]

for fund in fundnames:
     if "SBI" in fund:
        processing_list.append(fund.lower()) 



plist=["Mirae Asset Large Cap Fund", "Mirae Asset Great Consumer Fund"]




# Find pages containing fund names
#fund_pages, content, content_pages=find_fund_pages(pdf,plist)
#for fund, pages in fund_pages.items():
#    if pages:
#        print(f"Found '{fund}' on pages: {', '.join(map(str, pages))}")

extract_text_and_tables(pdf, 24)