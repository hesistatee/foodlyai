import enum
from datetime import date, datetime
from typing import final

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils.formulas import harris_benedict_formula


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

    fitness_profile: Mapped["FitnessProfile"] = relationship(
        "FitnessProfile", back_populates="user"
    )
    foods: Mapped[list["Food"]] = relationship("Food", back_populates="user")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")

    @property
    def subscription_is_active(self):
        return datetime.now() < self.subscription_end


@final
class FitnessProfile(Base):
    __tablename__ = "fitness_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    current_weight: Mapped[int] = mapped_column(nullable=False)
    desired_weight: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), onupdate=datetime.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="fitness_profile")

    @property
    def calorie_norm_for_weight_loss(self) -> int:
        return harris_benedict_formula(
            self.current_weight, self.height, self.age, self.gender
        )


@final
class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32))
    calories: Mapped[int] = mapped_column(nullable=False)
    protein: Mapped[int] = mapped_column(nullable=False)
    fat: Mapped[int] = mapped_column(nullable=False)
    carbs: Mapped[int] = mapped_column(nullable=False)

    number_of_servings: Mapped[int] = mapped_column(nullable=False, default=1)

    last_eaten_at: Mapped[date] = mapped_column(default=date.today())

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), onupdate=datetime.now()
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    user: Mapped["User"] = relationship("User", back_populates="foods")


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
