"""
PDF Reader for Yes Bank Credit Card Statement
"""

import os
import re
from datetime import datetime
from typing import List

import pymupdf

from config import config
from goodcat import goodcat
from models import Transaction


class YesBankCCPDFReader:
    """
    This is a simple PDF reader for Yes Bank Credit Card statements.
    It extracts transaction details such as date, description, reference number,
    and amount from the PDF file.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.all_transactions: List[Transaction] = []
        self.doc = None

    def __line_starts_with_date(self, input_line: str) -> bool:
        return re.match(r"^(\d{2}\/\d{2}\/\d{4})", input_line) is not None

    def __line_has_two_dates(self, input_line: str) -> bool:
        return (
            re.match(r"^(\d{2}\/\d{2}\/\d{4}) To (\d{2}\/\d{2}\/\d{4})", input_line)
            is not None
        )

    def __get_transaction_info(self, input_line):
        pattern = (
            r"^(\d{2}\/\d{2}\/\d{4})\s+(.*?)(?= - Ref No:)\s+- Ref No:\s*([A-Z0-9]*)"
        )

        match = re.match(pattern, input_line)

        if not match:
            raise AttributeError("Invalid transaction line format")

        date_str = match.group(1)
        description = match.group(2)
        ref_no = match.group(3)

        return date_str, description, ref_no

    def __read_pdf(self):
        lines = []

        for page in self.doc:
            text = page.get_text()
            lines.extend(text.strip().split("\n"))

        found_transaction = False

        i: int = 0
        net_spend: int = 0

        cnt = 1

        temp_dt = None
        temp_desc = None
        temp_amount = None

        while i < len(lines):
            line = lines[i].strip()

            if "End of the Statement" in line:
                break

            if self.__line_starts_with_date(line):
                if self.__line_has_two_dates(
                    line
                ):  # Avoiding as this is not a transaction
                    i += 1
                    continue

                try:
                    exp_dt_str, temp_desc, _ = self.__get_transaction_info(line)
                    temp_dt = datetime.strptime(exp_dt_str, "%d/%m/%Y").date()
                    found_transaction = True
                except AttributeError:
                    found_transaction = False
            else:
                if found_transaction and ("Dr" in line or "Cr" in line):
                    vals = line.replace(",", "").split(" ")

                    if len(vals) != 2:
                        i += 1
                        continue

                    if "Dr" in line:
                        temp_amount = float(vals[0])
                    elif "Cr" in line:
                        # exp_amount = float(vals[0]) # Ignoring credit for now
                        temp_amount = 0

                    temp_category = goodcat.get_category_fuzzy(temp_desc)
                    trans_obj = Transaction(
                        dt=temp_dt,
                        desc=temp_desc,
                        amount=temp_amount,
                        category=temp_category,
                    )
                    net_spend += trans_obj.amount

                    if temp_amount != 0:
                        self.all_transactions.append(trans_obj)
                        cnt += 1

                    temp_dt = None
                    temp_desc = None
                    temp_amount = None
            i += 1

        # print("Net Spend: ", net_spend) #TODO: compare net spend and add statement duration

    def __create_password(self) -> str:
        password = (
            config.name.replace(" ", "").lower()[0:4].upper()
            + f"{config.date_of_birth.day:02d}"
            + f"{config.date_of_birth.month:02d}"
        )

        return password

    def parse_document(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        self.doc = pymupdf.open(self.file_path)
        password = self.__create_password()
        self.doc.authenticate(password)

        self.__read_pdf()

        self.doc.close()

    def get_transactions(self) -> List[Transaction]:
        return self.all_transactions


if __name__ == "__main__":
    obj = YesBankCCPDFReader("kiwi_cc_20250507.pdf")
    obj.parse_document()
