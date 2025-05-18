from datetime import date, datetime
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    date_of_birth: date
    hdfc_cc_file: str
    yes_bank_cc_file: str
    name: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value: str) -> date:
        try:
            date_obj = datetime.strptime(value, "%d/%m/%Y").date()

            return date_obj
        except ValueError as exc:
            raise ValueError("Date of birth must be in the format dd/mm/yyyy") from exc

config = Config()
