"""
PDF Reader for Yes Bank Credit Card Statement
"""
from datetime import datetime
import re
import os

import pymupdf

from config import config

class YesBankCCPDFReader:
    """
    This is a simple PDF reader for Yes Bank Credit Card statements.
    It extracts transaction details such as date, description, reference number,
    and amount from the PDF file.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = None

    def __line_starts_with_date(self, input_line: str) -> bool:
        return re.match(r"^(\d{2}\/\d{2}\/\d{4})", input_line) is not None

    def __line_has_two_dates(self, input_line: str) -> bool:
        return re.match(r"^(\d{2}\/\d{2}\/\d{4}) To (\d{2}\/\d{2}\/\d{4})", input_line) is not None

    def __get_transaction_info(self, input_line):
        pattern = r"^(\d{2}\/\d{2}\/\d{4})\s+(.*?)(?= - Ref No:)\s+- Ref No:\s*([A-Z0-9]*)"

        match = re.match(pattern, input_line)

        if not match:
            raise AttributeError("Invalid transaction line format")

        date_str = match.group(1)
        description = match.group(2)
        ref_no = match.group(3)

        return date_str, description, ref_no

    def __parse_document(self):
        lines = []

        for page in self.doc:
            text = page.get_text()
            lines.extend(text.strip().split('\n'))

        found_transaction = False

        i: int = 0
        net_spend: int = 0

        class CurrentTransaction:
            exp_dt: datetime = None
            exp_desc: str = None
            exp_ref_no: str = None
            exp_amount: float = None

            def __str__(self):
                return f"Date: {self.exp_dt}, Description: {self.exp_desc}, \
                    Ref No: {self.exp_ref_no}, Amount: {self.exp_amount}"

        trans_obj = CurrentTransaction()

        cnt = 1
        while i < len(lines):
            line = lines[i].strip()

            if "End of the Statement" in line:
                break

            #print(line)

            if self.__line_starts_with_date(line):
                if self.__line_has_two_dates(line): # Avoiding as this is not a transaction
                    i += 1
                    continue

                try:
                    exp_dt_str, trans_obj.exp_desc, trans_obj.exp_ref_no \
                        = self.__get_transaction_info(line)
                    trans_obj.exp_dt = datetime.strptime(exp_dt_str, "%d/%m/%Y").date()
                    found_transaction = True
                except AttributeError:
                    found_transaction = False
            else:
                if found_transaction and ("Dr" in line or "Cr" in line):
                    vals = line.replace(',', '').split(" ")

                    if len(vals) != 2:
                        i += 1
                        continue

                    if "Dr" in line:
                        trans_obj.exp_amount = -float(vals[0])
                    elif "Cr" in line:
                        #exp_amount = float(vals[0]) # Ignoring credit for now
                        trans_obj.exp_amount = 0

                    net_spend += trans_obj.exp_amount

                    print(trans_obj)
                    cnt += 1

                    trans_obj = CurrentTransaction()

            i += 1

        print("Net Spend: ", net_spend)

    def __create_password(self) -> str:
        password = config.name.replace(" ", "").lower()[0:4].upper() + \
        f"{config.date_of_birth.day:02d}" + \
        f"{config.date_of_birth.month:02d}"

        return password

    def read_pdf(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        self.doc = pymupdf.open(self.file_path)
        password = self.__create_password()
        self.doc.authenticate(password)

        self.__parse_document()

        self.doc.close()


if __name__ == "__main__":
    obj = YesBankCCPDFReader("kiwi_cc_20250507.pdf")
    obj.read_pdf()
