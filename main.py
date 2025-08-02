import parsers.hdfc_cc as hdfc_cc_parser
import parsers.yes_bank_cc as yes_bank_cc_parser
from config import config
#from goodcat import GoodCat

if __name__ == "__main__":
    # HDFC Credit Card Reader
    hdfc_reader = hdfc_cc_parser.HdfcCcExcelReader(config.hdfc_cc_file)
    hdfc_reader.parse_document()
    hdfc_transactions = hdfc_reader.get_transactions()

    for trans in hdfc_transactions:
        print(trans)

    #print(hdfc_transactions)

    # Yes Bank Credit Card Reader
    yes_bank_reader = yes_bank_cc_parser.YesBankCCPDFReader(config.yes_bank_cc_file)
    yes_bank_reader.parse_document()
    yes_transactions = yes_bank_reader.get_transactions()

    for trans in yes_transactions:
        print(trans)
    #print(yes_transactions)

    #obj = GoodCat()
    #for tr in yes_transactions:
    #    print(tr.tr_dt, tr.tr_desc, tr.tr_amount, obj.get_category_fuzzy(tr.tr_desc))

