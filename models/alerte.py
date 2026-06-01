from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from models.warehouse import Warehouse
from models.lot import Lot


class Alerte(Base):
    __tablename__ = 'alerte'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey('warehouse.id'), nullable=False)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey('lot.id'), nullable=False)
    alerte_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="alertes")
    lot: Mapped["Lot"] = relationship("Lot", back_populates="alertes")