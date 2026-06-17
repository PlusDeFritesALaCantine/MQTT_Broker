from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class IotSensor(Base):
    __tablename__ = 'sensor'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey('warehouse.id'), nullable=False)
    mqtt_topic: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    warehouse: Mapped[Warehouse] = relationship("Warehouse", back_populates="sensors")
    readings: Mapped[list[SensorReading]] = relationship("SensorReading", back_populates="sensor")
