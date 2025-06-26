from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
from routers.routes import router
from internal import status
from internal.logger import logger



origins = [
    "http://localhost:3000"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Call DB check via status (and in future: other services too)
    logger.info("Starting up GSBAN Console API v0.1")
    status.startup()
    yield
    logger.info("Shutting down API...")



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# call routers here
app.include_router(router, prefix="/api/v1", tags=["GSBAN Console API"])
