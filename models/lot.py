from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.alerte import Alerte
    from models.warehouse import Warehouse


class Lot(Base):
    __tablename__ = 'lot'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lot_code: Mapped[str] = mapped_column(String(50), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey('warehouse.id'), nullable=False)
    stored_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    warehouse: Mapped[Warehouse] = relationship("Warehouse", back_populates="lots")
    alertes: Mapped[list[Alerte]] = relationship("Alerte", back_populates="lot")
