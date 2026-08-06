from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.base import UserCreate, UserOut, UserUpdate
from src.services.user_service import UserService
