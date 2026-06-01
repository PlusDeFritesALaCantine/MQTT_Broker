from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ideal_temperature: Mapped[int] = mapped_column(Integer, nullable=False)
    ideal_humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    temperature_tolerance: Mapped[int] = mapped_column(Integer, nullable=False)
    humidity_tolerance: Mapped[int] = mapped_column(Integer, nullable=False)

    exploitations: Mapped[list["Exploitation"]] = relationship("Exploitation", back_populates="country")