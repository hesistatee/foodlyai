from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int]
    username: Mapped[str] = mapped_column(String(32))
    number_of_requests: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    has_subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    subscription_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    
    def is_subscription_active(self) -> bool:
        if not self.has_subscription:
            return False
        elif self.has_subscription and datetime.now() > self.subscription_end:
            self.has_subscription = False
            return False
        return datetime.now() < self.subscription_end
    