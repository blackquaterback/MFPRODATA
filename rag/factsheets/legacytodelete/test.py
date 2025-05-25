import camelot
import PyPDF2

def extract_tables_and_text(pdf_path):
    # Extract tables
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    
    # Extract text
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    # Print extracted tables
    for i, table in enumerate(tables):
        print(f"Table {i+1}:")
        print(table.df)
        print("\n")
    
    # Print extracted text
    print("Extracted Text:")
    print(text)

# Example usage
extract_tables_and_text("/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/one.pdf")
