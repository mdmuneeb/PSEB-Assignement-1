
from fastapi import FastAPI

from app.routes.rates import router as rates_router

app = FastAPI(
    title="Currency Exchange API",
    description="Live and historical currency exchange rates powered by AllRatesToday.",
    version="1.0.0",
)

app.include_router(rates_router)


@app.get("/")
async def root():
    return {
        "message": "Currency Exchange API is running!",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
