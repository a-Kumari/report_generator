from fastapi import FastAPI
from database import engine, Base
from routers import auth, user, reports

app = FastAPI()

app.include_router(auth.router, tags=["Authentication"])
app.include_router(user.router, tags=["Users"])
app.include_router(reports.router, tags=["Reports"])
