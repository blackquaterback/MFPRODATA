import os
from portfolio.parser import * #this will import all the parsers from the parser module



if __name__ == "__main__":
     


    # set the base dir
    base_dir = "/Users/njp60/Documents/code/mutualfundbackend/funddata/data2/"

    # List of AMC names
    amc_names = [
        "360 One Asset Management", "Aditya Birla Sun Life Mutual Fund", "Axis Mutual Fund", 
        "Bandhan Mutual Fund", "Bank of India Mutual Fund", "Baroda BNP Paribas Mutual Fund", 
        "Canara Robeco Mutual Fund", "DSP Mutual Fund", "Edelweiss Mutual Fund", "Franklin Templeton India", 
        "Groww Mutual Fund", "HDFC Mutual Fund", "Helios Mutual Fund", "HSBC Mutual Fund", 
        "ICICI Prudential Mutual Fund", "Invesco Mutual Fund", "ITI Mutual Fund", "JM Financial Mutual Fund", 
        "Kotak Mutual Fund", "LIC Mutual Fund", "Mahindra Manulife Mutual Fund", "Mirae Asset Mutual Fund", 
        "Motilal Oswal Mutual Fund", "Navi Mutual Fund", "Nippon India Mutual Fund", "NJ Mutual Fund", 
        "PGIM India Mutual Fund", "PPFAS Mutual Fund", "Quant Mutual Fund", "Quantum Mutual Fund", 
        "SBI Mutual Fund", "Shriram Mutual Fund", "Sundaram Mutual Fund", "Tata Mutual Fund", 
        "Trust Mutual Fund", "Union Mutual Fund", "UTI Mutual Fund", "WhiteOak Mutual Fund", 
        "Zerodha Fund House"
    ]

    # Create a directory for each AMC
    for amc in amc_names:
        
        match amc:

    
            case "Parag Parikh Mutual Fund":
            # Process Parag Parikh Mutual Fund
                amc_dir = os.path.join(base_dir, amc)
                parser = ParagParikhParser(amc_dir)
                output_df = parser.process()
                output_df.to_excel(os.path.join(amc_dir, "output.xlsx"), index=False)
                print(f"Processed {amc} and saved to {amc_dir}/output.xlsx")


            case "HDFC Mutual Fund":
            # Process Parag Parikh Mutual Fund
                amc_dir = os.path.join(base_dir, amc)

                #create HDFC parser 
              
            case "ICICI Prudential Mutual Fund":
            # Process Parag Parikh Mutual Fund
                amc_dir = os.path.join(base_dir, amc)

                #create ICICI parser 
            case "ICICI Prudential Mutual Fund":
            # Process Parag Parikh Mutual Fund
                amc_dir = os.path.join(base_dir, amc)

                #create ICICI parser 


        
              
