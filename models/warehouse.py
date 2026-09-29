from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.alerte import Alerte
    from models.exploitation import Exploitation
    from models.iot_sensor import IotSensor
    from models.lot import Lot


class Warehouse(Base):
    __tablename__ = 'warehouse'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exploitation_id: Mapped[int] = mapped_column(Integer, ForeignKey('exploitation.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    manager_mail: Mapped[str] = mapped_column(String(100), nullable=False)

    exploitation: Mapped[Exploitation] = relationship("Exploitation", back_populates="warehouses")
    lots: Mapped[list[Lot]] = relationship("Lot", back_populates="warehouse")
    sensors: Mapped[list[IotSensor]] = relationship("IotSensor", back_populates="warehouse")
    alertes: Mapped[list[Alerte]] = relationship("Alerte", back_populates="warehouse")
