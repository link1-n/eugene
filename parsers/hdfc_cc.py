"""
Module to read HDFC credit card statements in .xls format
"""
import os
from typing import List
from datetime import datetime

import pandas as pd

from goodcat import goodcat
from models import Transaction

class HdfcCcExcelReader:
    """
    Module to read HDFC credit card statements in .xls format
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.all_transactions: List[Transaction] = []

    def __parse_date(self, date_str):
        formats = ['%d/%m/%Y %H:%M:%S', '%d/%m/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Time data '{date_str}' does not match any supported format.")

    def __read_excel(self):
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
                date_obj = self.__parse_date(str(row[17]).strip())
                description = str(row[21]).strip()
                amount = float(str(row[48]).strip().replace(',', ''))
                dr_cr = str(row[54]).strip()

                if dr_cr == "Cr":
                    continue

                temp_category = goodcat.get_category_fuzzy(description)
                trans_obj = Transaction(
                    dt=date_obj,
                    desc=description,
                    amount=amount,
                    category=temp_category
                )

                self.all_transactions.append(trans_obj)
    def parse_document(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        self.__read_excel()

    def get_transactions(self) -> List[Transaction]:
        return self.all_transactions

if __name__ == "__main__":
    hdfc_reader = HdfcCcExcelReader("BilledStatements_7096_14-05-25_14.07.xls")
    hdfc_reader.parse_document()
