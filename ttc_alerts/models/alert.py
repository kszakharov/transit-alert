from pydantic import BaseModel, Field, AliasPath, field_validator


class TTCAlert(BaseModel):
    header: str = Field(alias=AliasPath("headerText", "translation", 0, "text"))
    description: str = Field(alias=AliasPath("descriptionText", "translation", 0, "text"))
    cause: str = Field(alias="cause")
    effect: str = Field(alias="effect")

    @field_validator("header")
    @classmethod
    def normalize_header(cls, v: str) -> str:
        return v.strip().removesuffix(": There i").removesuffix(" f").removesuffix(" v")

    def format(self) -> str:
        """Format the alert for display."""

        return f"Header: {self.header}\nDescription: {self.description}\nCause: {self.cause}\nEffect: {self.effect}"

    def __str__(self) -> str:
        return f"Header: {self.header}, Description: {self.description}"
