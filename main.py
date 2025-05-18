import parsers.hdfc_cc as hdfc_cc_parser
import parsers.yes_bank_cc as yes_bank_cc_parser
from config import config

if __name__ == "__main__":
    # HDFC Credit Card Reader
    hdfc_reader = hdfc_cc_parser.HdfcCcExcelReader(config.hdfc_cc_file)
    hdfc_reader.parse_file()

    # Yes Bank Credit Card Reader
    yes_bank_reader = yes_bank_cc_parser.YesBankCCPDFReader(config.yes_bank_cc_file)
    yes_bank_reader.read_pdf()
