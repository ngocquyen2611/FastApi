from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


# 9. ORDER (Đơn hàng)
class Order(Base):
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    payment_status = Column(Boolean, default=False)

    user = relationship("User", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")


# 10. ORDER_DETAIL (Chi tiết đơn hàng)
class OrderDetail(Base):
    __tablename__ = "order_detail"

    order_id = Column(Integer, ForeignKey("order.order_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")