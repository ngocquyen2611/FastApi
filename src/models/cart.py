from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


# 7. CART_ITEM (Giỏ hàng)
class CartItem(Base):
    __tablename__ = "cart_item"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")  