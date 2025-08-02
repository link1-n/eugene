from datetime import date
from pydantic import BaseModel

class Transaction(BaseModel):
    dt: date
    desc: str
    amount: float
    category: str

    def __str__(self):
        ret_str = f"Date: {self.dt}, Description: {self.desc}," + \
        f" Amount: {self.amount}, Category: {self.category}"

        return ret_str
