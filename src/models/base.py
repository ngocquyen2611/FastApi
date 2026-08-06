from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from src.core.database import Base 

# 1. USER
class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    # Relationships
    user_detail = relationship("UserDetail", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user")


# 2. USER_DETAIL (Quan hệ 1:1 với User)
class UserDetail(Base):
    __tablename__ = "user_detail"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    phone = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True)
    address = Column(String, nullable=True)
    password = Column(String, nullable=False)

    user = relationship("User", back_populates="user_detail")


# 3. CATEGORY
class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    product_categories = relationship("ProductCategory", back_populates="category")


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


# 5. PRODUCT_CATEGORY (Bảng trung gian N:M)
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


# 7. CART_ITEM (Giỏ hàng)
class CartItem(Base):
    __tablename__ = "cart_item"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


# 8. WISHLIST_ITEM (Danh sách yêu thích)
class WishlistItem(Base):
    __tablename__ = "wishlist_item"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("product.product_id"), primary_key=True)
    added_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")


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