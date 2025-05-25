import fitz  # PyMuPDF
import pdfplumber
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from unstructured.partition.pdf import partition_pdf
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import re
import pandas as pd
import io
import os
import json


def format_table_to_text(tables):
    """Convert extracted tables into structured text format."""
    formatted_text = ""
    
    for i, table in enumerate(tables, start=1):
        #formatted_text += f"\n🔹 **Table {i}:**\n"
        for row in table:
            # Remove extra spaces, replace empty cells with '-'
            cleaned_row = [cell.strip() if cell else "" for cell in row]
            formatted_text += " | ".join(cleaned_row) + "\n"

    return formatted_text.strip()

class FundDocumentProcessor:
    def __init__(self, pdf_path,  vector_store_path):
        self.embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.vector_store_path = vector_store_path
        self.vector_store = None
        self.pdf_path=pdf_path
        print("Initialized FundDocumentProcessor with model:", self.embedding_model_name)

    def process_pdfs(self, pdf_folder):
        fund_texts = ""
        for filename in os.listdir(pdf_folder):
            if filename.endswith(".pdf"):
                print(f"Processing PDF: {filename}")
                fund_texts +=self.extract_text_from_pdf(os.path.join(pdf_folder, filename))
        return fund_texts

    def extract_text_from_pdf(self, pdf):
        """Extract text from PDF mutual fund document"""
        text = ""
        print(f"Extracting text from PDF: {pdf}")
        with pdfplumber.open(pdf) as pdf:
            for page in pdf.pages:
                
                page_text=""
                page_tables=None
               
                extracted_tables = page.extract_tables()
                if extracted_tables:
                    print(f"📊 {len(extracted_tables)} tables found on page")
                    page_tables=format_table_to_text(extracted_tables)
                
                extracted_text = page.extract_text()

                if extracted_text:
                    page_text += extracted_text + "\n"

                if page_tables is not None:
                    page_text+=page_tables+"\n"
                
                if page_text:
                    text += page_text + "\n"            
        print("Text extraction completed.")
        return text
        
    def create_embedding(self, fund_texts):
        """Create vector embeddings from extracted fund texts."""
        print("Creating text embeddings...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.create_documents([fund_texts])
        doc_embeddings = self.embedding_model.embed_documents([doc.page_content for doc in docs])
        print("Embeddings created.")
        return docs, doc_embeddings

    def create_vector_store(self, docs):
        """Create and save FAISS vector store."""
        print("Creating FAISS vector store...")
        self.vector_store = FAISS.from_documents(docs, self.embedding_model)
        self.vector_store.save_local(self.vector_store_path)
        print("Vector store created and saved at:", self.vector_store_path)

    def load_vector_store(self):
        """Load FAISS vector store from disk."""
        print("Loading FAISS vector store...")
        self.vector_store = FAISS.load_local(self.vector_store_path, self.embedding_model, allow_dangerous_deserialization=True)
        print("Vector store loaded.")
        return self.vector_store.as_retriever()

    def get_retriever(self):
        """Return retriever from the loaded FAISS vector store."""
        if self.vector_store is None:
            self.load_vector_store()
        print("Retriever ready.")
        return self.vector_store.as_retriever(search_kwargs={"k": 5})
    
    def create_rag_chain(self):
        """Create a RAG pipeline using Ollama and the retriever."""
        print("Setting up RAG pipeline...")
        retriever = self.get_retriever()
        llm = Ollama(model="llama3.1")  # Replace with local model
        rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        print("RAG pipeline is ready.")
        return rag_chain
    
    def test_retriever(self, query):
        """Test retriever with a sample query."""
        print(f"Testing retriever with query: {query}")
        retriever = self.get_retriever()
        results = retriever.get_relevant_documents(query)

        if results:
            print("\nRetrieved Documents:")
            for i, doc in enumerate(results, 1):
                print(f"\n🔹 Result {i}: {doc.page_content[:500]}...")  # Display first 500 chars
        else:
            print("No relevant documents found.")


# Example usage:
# processor = FundDocumentProcessor()
# text = processor.extract_text_from_pdf("example.pdf")
# docs, embeddings = processor.create_embedding(text)
# processor.create_vector_store(docs)
# retriever = processor.get_retriever()

if __name__ == "__main__":

    # Example Usage
    fund_name = "Mirae Asset Large Cap Fund"
    pdf_path = "/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/"
    vector_store = "/Users/njp60/Documents/code/mutualfundbackend/funddata/factsheets/vector_store.faiss"

    processor = FundDocumentProcessor(pdf_path=pdf_path, vector_store_path=vector_store)

    #text = processor.process_pdfs(processor.pdf_path)
    #docs, embeddings = processor.create_embedding(text)
    #processor.create_vector_store(docs)
    qa_chain = processor.create_rag_chain()


    fund_names=["Mirae Asset Large Cap Fund","Mirae Asset Great Consumer Fund" , "SBI Bluechip Fund"]

    for fund_name in fund_names:
       
       query = f"""
    Extract details for the mutual fund named "{fund_name}".

    Required details:
    - Fund Name
    - AMC (Asset Management Company)
    - Expense Ratio (Direct & Regular Plans)
    - Inception Date
    - Fund Manager(s)
    - Fund Objective
    - Fund Type (Equity, Debt, Hybrid, etc.)
    - Exit Load
    - Risk Level (Riskometer)

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



       ans=qa_chain.invoke(query)
 
    