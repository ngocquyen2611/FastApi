from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


# 4. PRODUCT
class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    product_categories = relationship("ProductCategory", back_populates="product")
    product_details = relationship("ProductDetail", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    order_details = relationship("OrderDetail", back_populates="product")


# 5. PRODUCT_CATEGORY (Bảng trung gian N:M giữa Product và Category)
class ProductCategory(Base):
    __tablename__ = "product_category"

    category_id = Column(Integer, ForeignKey("category.category_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)

    category = relationship("Category", back_populates="product_categories")
    product = relationship("Product", back_populates="product_categories")


# 6. PRODUCT_DETAIL (Biến thể sản phẩm: size, color...)
class ProductDetail(Base):
    __tablename__ = "product_detail"

    product_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    stock_quantity = Column(Integer, default=0)
    size = Column(Integer, nullable=True)
    color = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)

    product = relationship("Product", back_populates="product_details")