import os
import pandas as pd
from datetime import datetime

def combine_portfolio_files():
    """
    Combines all Excel files from the upload/portfolio directory into a single Excel file.
    The combined file will be saved in the upload directory with a timestamp.
    """
    # Create upload and portfolio directories if they don't exist
    upload_dir = os.path.join(os.getcwd(), "upload")
    portfolio_dir = os.path.join(upload_dir, "portfolio")
    
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(portfolio_dir, exist_ok=True)

    # Get all Excel files from the portfolio directory
    excel_files = []
    for file in os.listdir(portfolio_dir):
        if file.endswith(('.xlsx', '.xls', '.xlsb')) and not file.startswith('~$'):  # Exclude temp Excel files
            excel_files.append(os.path.join(portfolio_dir, file))

    if not excel_files:
        print("⚠️ No Excel files found in upload/portfolio directory")
        return

    # Combine all Excel files
    all_data = pd.DataFrame()
    
    for file in excel_files:
        try:
            print(f"📖 Reading {os.path.basename(file)}...")
            if file.endswith('.xlsb'):
                df = pd.read_excel(file, engine='pyxlsb')
            else:
                df = pd.read_excel(file)
            
            # Add source file information
            df['Source File'] = os.path.basename(file)
            
            # Concatenate to main dataframe
            all_data = pd.concat([all_data, df], ignore_index=True)
            print(f"✅ Successfully processed {os.path.basename(file)}")
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(file)}: {str(e)}")
            continue

    if all_data.empty:
        print("❌ No data could be processed from the Excel files")
        return

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(upload_dir, f"all_portfolios_{timestamp}.xlsx")

    # Save combined data
    try:
        all_data.to_excel(output_file, index=False)
        print(f"\n✨ Successfully combined {len(excel_files)} files into: {output_file}")
        print(f"📊 Total rows: {len(all_data)}")
        
        # Display column statistics
        print("\n📋 Column Summary:")
        for column in all_data.columns:
            non_null_count = all_data[column].count()
            print(f"   - {column}: {non_null_count} non-null values")
            
    except Exception as e:
        print(f"❌ Error saving combined file: {str(e)}")

if __name__ == "__main__":
    print("🔄 Starting portfolio combination process...")
    combine_portfolio_files()
    print("\n✅ Process completed!") 