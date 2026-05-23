from sqlalchemy import Column, ForeignKey, Table

from app.db.session import Base

order_addresses = Table(
    "order_addresses",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "address_id",
        ForeignKey("addresses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
