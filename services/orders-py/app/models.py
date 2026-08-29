"""Pydantic models for the orders service."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app.pricing import order_total


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(default=1, gt=0)
    unit_price: float = Field(gt=0)


class OrderBase(BaseModel):
    customer_email: EmailStr
    items: list[OrderItem] = Field(min_length=1)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: OrderStatus


class OrderRead(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    created_at: datetime

    @computed_field
    @property
    def total(self) -> float:
        return order_total(self.items)
