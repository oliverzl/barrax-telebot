from datetime import date
from typing import Optional


class ProjectCode:
    def __init__(self):
        self._natureCode: Optional[int] = None
        self._date: Optional[date] = None
        self._countryCode: Optional[int] = None
        self._name: Optional[str] = None
        self._runningNum: Optional[int] = " "

    def set_nature_code(self, nature: int):
        self._natureCode = nature

    def set_date(self, nume: date):
        self._date = nume

    def set_country_code(self, country: int):
        self._countryCode = country

    def set_name(self, name: str):
        self._name = name

    def set_running_num(self, num: int):
        self._runningNum = num

    def get_details(self) -> str:
        reformatted_date = self._date.strftime("%d/%m/%y")
        country = ""
        if self._countryCode == "65":
            country = "SINGAPORE"
        else:
            country = "CAMBODIA"

        return (
            f"NATURE: {self._natureCode}\n"
            f"OPEN DATE: {reformatted_date}\n"
            f"COUNTRY: {country}\n"
            f"PROJECT NAME/ADDRESS: {self._name}\n"
            f"RUNNING NUMBER:"
        )

    def __str__(self):
        month = None
        year = None
        if self._date is not None:
            day = self._date.strftime("%d")
            month = self._date.strftime("%m")
        
            year = self._date.strftime("%y")

        return f"{self._countryCode}-{self._natureCode}-{day}-{month}-{year}-{self._name}-{self._runningNum}"
