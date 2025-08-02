"""
A module to help categorize payments.
"""

from typing import Dict, List
from pathlib import Path
import re
from rapidfuzz import fuzz, process
from config import config


class GoodCat:
    def __init__(self):
        print("Initialising GoodCat")
        self.keywords: Dict[str, List[str]] = {}
        self.compiled_patterns = {}
        self.merchant_to_category = {}
        self.__read_keywords()

    def __read_keywords(self):
        directory = Path(config.category_folder_path)

        self.keywords = {}

        for txt_file in directory.glob("*.txt"):
            with txt_file.open("r") as f:
                self.keywords[str(txt_file.name).strip().split(".")[0]] = [
                    line.strip() for line in f
                ]  # TODO: use regex here

        for category, keywords in self.keywords.items():
            pattern = (
                r"\b("
                + "|".join(re.escape(keyword.lower()) for keyword in keywords)
                + r")\b"
            )
            self.compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)

        self.merchant_to_category = {
            merchant_name.lower(): category
            for category, merchants in self.keywords.items()
            for merchant_name in merchants
        }

        print(f"found categories: {self.keywords.keys()}")

    def get_category_fuzzy(self, text: str, threshold: int = 80) -> str:
        text = text.lower()

        match, score, _ = process.extractOne(
            text,
            self.merchant_to_category.keys(),
            scorer=fuzz.partial_ratio,  # good for substrings like "payment to zomato"
        )

        if match and score >= threshold:
            return self.merchant_to_category[match]
        return "other"

    def get_category_regex(self, payment_str):
        category_scores = {}
        for category, pattern in self.compiled_patterns.items():
            matches = pattern.findall(payment_str)
            category_scores[category] = len(matches)

        print(category_scores)
        if category_scores and max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        return "other"


goodcat = GoodCat()


if __name__ == "__main__":
    obj = GoodCat()
    print(obj.get_category_regex("payment to uber_systems"))
    print(obj.get_category_fuzzy("payment to uber_systems"))
