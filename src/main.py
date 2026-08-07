from fastapi import FastAPI

from src.api.v1 import users
from src.core.database import init_db

app = FastAPI(title="My FastAPI Base", description="A base template for FastAPI applications", version="1.0.0")

init_db()


@app.get("/")
async def root():
    return {"message": "Welcome to My FastAPI Base!"}