from pydantic import BaseModel, Field, AliasPath, field_validator
from typing import Self


BAD_SUFFIXES: list[str] = [
    ": There i",
    " f",
    " v",
    " vi",
]


class TTCAlert(BaseModel):
    header: str = Field(validation_alias=AliasPath("headerText", "translation", 0, "text"))
    description: str = Field(validation_alias=AliasPath("descriptionText", "translation", 0, "text"))

    def __hash__(self) -> int:
        return hash((self.header, self.description))

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, TTCAlert):
            return NotImplemented
        return self.header == other.header and self.description == other.description

    @field_validator("header")
    @classmethod
    def normalize_header(cls, v: str) -> str:
        for bad_suffix in BAD_SUFFIXES:
            v = v.removesuffix(bad_suffix)
        return v

    def model_post_init(self, __context) -> None:
        if self.description.startswith(self.header):
            self.header = self.header.split(": ", 1)[0]
            self.description = self.description.split(": ", 1)[1]

    def format(self) -> str:
        """Format the alert for display."""

        return f"Header: {self.header}\nDescription: {self.description}"

    def __str__(self) -> str:
        return f"Header: {self.header}, Description: {self.description}"
