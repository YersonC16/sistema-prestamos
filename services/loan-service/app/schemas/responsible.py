from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
DocumentNumber = Annotated[str, StringConstraints(strip_whitespace=True, min_length=4, max_length=30)]
DocumentType = Literal["CC", "TI", "CE", "PASAPORTE"]


class ResponsibleCreate(BaseModel):
    full_name: FullName
    document_type: DocumentType
    document_number: DocumentNumber
    phone: str | None = None

    @field_validator("document_number")
    @classmethod
    def only_digits_and_letters(cls, value: str) -> str:
        cleaned = value.replace(" ", "").replace("-", "")
        if not cleaned.isalnum():
            raise ValueError("El número de documento solo puede tener letras y números")
        return cleaned

    @field_validator("phone")
    @classmethod
    def empty_phone_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ResponsibleUpdate(BaseModel):
    full_name: FullName | None = None
    phone: str | None = None
    is_active: bool | None = None


class ResponsibleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    document_type: str
    document_number: str
    phone: str | None = None
    is_active: bool