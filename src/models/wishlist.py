from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


# 8. WISHLIST_ITEM (Danh sách yêu thích)
class WishlistItem(Base):
    __tablename__ = "wishlist_item"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    added_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")