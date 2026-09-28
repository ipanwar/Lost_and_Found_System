from enum import Enum
from typing import Optional
from pydantic import field_validator
from sqlmodel import Field, SQLModel


class ItemStatus(str, Enum):
    LOST = "Lost"
    FOUND = "Found"
    RETURNED = "Returned"


class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, description="Name/title of the item")
    description: str = Field(min_length=1, max_length=1000, description="Detailed description of the item")
    category: str = Field(min_length=1, max_length=100, description="Category such as Electronics, Documents, Accessories, etc.")
    location: str = Field(min_length=1, max_length=200, description="Location where the item was lost or found")
    reported_by: str = Field(min_length=1, max_length=100, description="Name of the person reporting the item")
    status: ItemStatus = Field(default=ItemStatus.LOST, description="Status of the item: Lost, Found, or Returned")

    @field_validator("title", "description", "category", "location", "reported_by")
    @classmethod
    def validate_non_empty_text(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field '{info.field_name}' cannot be empty or contain only whitespace.")
        return v.strip()


class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique item identifier")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Name/title of the item")
    description: Optional[str] = Field(default=None, min_length=1, max_length=1000, description="Detailed description of the item")
    category: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Category of the item")
    location: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Location where the item was lost/found")
    reported_by: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Name of the person reporting")
    status: Optional[ItemStatus] = Field(default=None, description="Status of the item: Lost, Found, or Returned")

    @field_validator("title", "description", "category", "location", "reported_by")
    @classmethod
    def validate_non_empty_text_when_provided(cls, v: Optional[str], info) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError(f"Field '{info.field_name}' cannot be empty or contain only whitespace.")
            return v.strip()
        return v


class ItemRead(ItemBase):
    id: int
