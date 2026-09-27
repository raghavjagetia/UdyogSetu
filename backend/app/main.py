from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine, SessionLocal
from .routers import applications, auth, dashboard, rules, schemes
from .seed_data import seed

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed(db)

app = FastAPI(title="UdyogSetu API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(rules.router)
app.include_router(schemes.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
