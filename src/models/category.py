from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import Base


# 3. CATEGORY
class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    product_categories = relationship("ProductCategory", back_populates="category")