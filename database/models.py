from datetime import datetime
import enum
from typing import final
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Enum, Text


class Base(DeclarativeBase):
    pass


class OrderStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentMethod(enum.Enum):
    STARS = "stars"
    YOOKASSA = "yookassa"


@final
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column()
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    number_of_requests: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    has_subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    subscription_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")

    def is_subscription_active(self) -> bool:
        if not self.has_subscription:
            return False
        elif self.has_subscription and datetime.now() > self.subscription_end:
            self.has_subscription = False
            return False
        return datetime.now() < self.subscription_end


@final
class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(64))
    price: Mapped[float] = mapped_column()
    payload: Mapped[str] = mapped_column(String(32))
    days: Mapped[int] = mapped_column()

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="tarrif")


@final
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))

    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), onupdate=datetime.now()
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    payment_id: Mapped[str] = mapped_column(String(128), nullable=True)
    payment_details: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    tarrif: Mapped["Tariff"] = relationship("Tariff", back_populates="orders")

    def is_completed(self) -> bool:
        return self.status == OrderStatus.COMPLETED

    def mark_as_completed(self) -> None:
        self.status = OrderStatus.COMPLETED
        self.completed_at = datetime.now()
