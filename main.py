from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import uvicorn

from app.database import init_db
from app.routes import stocks, analytics, predictions
from app.routes import assignment_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="JarNox Stock Intelligence Dashboard",
    description="A mini financial data platform for NSE Indian stocks with real-time insights and ML predictions.",
    version="1.0.0",
    lifespan=lifespan
)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(stocks.router, tags=["Market Data"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(predictions.router, tags=["Predictions"])
app.include_router(assignment_routes.router, tags=["Assignment APIs"])

@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse("templates/index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)