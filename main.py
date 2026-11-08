from fastapi import FastAPI
import models
from database import engine
from routers import categories, expenses, users, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(categories.router)
app.include_router(auth.router)

