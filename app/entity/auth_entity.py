from datetime import datetime
from typing import List,Optional

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_details"

    id = mapped_column(Integer, primary_key=True)
    username: Mapped[str]
    password_hash: Mapped[str]
    create_date: Mapped[Optional[datetime]] = mapped_column(insert_default=func.now())
    signupoptions: Mapped[List["signupoptions"]] = relationship(back_populates="user_details")


class signupoptions(Base):
    __tablename__ = "signupoptions"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("user_details.id"))
    platform : Mapped[str]
    user: Mapped["User"] = relationship(back_populates="signupoptions")