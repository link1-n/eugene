"""
Module to read HDFC credit card statements in .xls format
"""
import pandas as pd

class HdfcCcExcelReader:
    """
    Module to read HDFC credit card statements in .xls format
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse_file(self):
        """
        Parses the HDFC credit card statement file and extracts transaction details.
        """
        df = pd.read_excel(self.file_path)

        df.columns = range(len(df.columns))

        found_transaction = False
        for i, row in df.iterrows():
            check_val = row[1]

            if pd.isna(check_val):
                found_transaction = False
                continue

            if check_val == "Transaction type":
                found_transaction = True
                continue

            if found_transaction:
                date = str(row[17]).strip()
                description = str(row[21]).strip()
                amount = str(row[48]).strip()
                dr_cr = str(row[54]).strip()

                print(f"Date: {date}, Description: {description}, Amount: {amount}, Dr/Cr: {dr_cr}")

if __name__ == "__main__":
    hdfc_reader = HdfcCcExcelReader("BilledStatements_7096_14-05-25_14.07.xls")
    hdfc_reader.parse_file()
